#!/usr/bin/env python3
"""Free daily price/score refresh for the Stock Picks tab (Tier 1).

Runs in the GitHub Action (pure Python + yfinance, no MCP, no cost). Reads the
existing data/micro.json — which already holds the research layer produced by the
MCP pipeline — refreshes ONLY the price-derived fields from fresh yfinance quotes,
recomputes each name's momentum sub-score + composite + group rank, and writes it
back. Every research field (thesis, evidence, fundamentals, analyst, exposure and
the non-momentum sub-scores) is left byte-for-byte untouched.

Cadence: the Action runs this 4×/day on trading days, so the tab's prices, momentum
and scores move at the same times as the live dashboard. The heavier research layer
is refreshed once a day pre-market by a separate Claude Routine (see
scripts/micro_refresh_research.md).
"""
import datetime
import json
import pathlib
import sys

import yfinance as yf

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from micro_score import momentum_score, composite_from_subs, rank_within_groups

DATA = pathlib.Path(__file__).resolve().parent.parent / "data"
CHUNK = 50


def compute_quote(closes):
    """From a 1y daily close series (pandas Series) → {price, vs50, vs200, range52w}.

    Mirrors the FMP-derived definitions the research snapshot was built with:
    vs50/vs200 = % vs the 50/200-day simple moving average, range52w = position of
    the last price within the trailing-year low→high band (0-100).
    """
    s = closes.dropna()
    if len(s) < 2:
        return None
    price = float(s.iloc[-1])
    out = {"price": round(price, 4)}
    if len(s) >= 50:
        ma50 = float(s.iloc[-50:].mean())
        out["vs50"] = round((price / ma50 - 1) * 100, 1) if ma50 else None
    if len(s) >= 200:
        ma200 = float(s.iloc[-200:].mean())
        out["vs200"] = round((price / ma200 - 1) * 100, 1) if ma200 else None
    lo, hi = float(s.min()), float(s.max())
    out["range52w"] = round((price - lo) / (hi - lo) * 100, 1) if hi > lo else None
    return out


def fetch_quotes(tickers):
    """Bulk-fetch 1y daily closes via yfinance, in chunks. Returns {ticker: quote}."""
    quotes = {}
    for i in range(0, len(tickers), CHUNK):
        batch = tickers[i:i + CHUNK]
        try:
            df = yf.download(batch, period="1y", auto_adjust=True,
                             progress=False, group_by="ticker", threads=True)
        except Exception as e:
            print(f"  chunk {i // CHUNK} download failed: {e}")
            continue
        for t in batch:
            try:
                # multi-ticker → columns are MultiIndex (ticker, field); single → flat
                closes = df[t]["Close"] if (t, "Close") in df.columns else (
                    df["Close"] if "Close" in df.columns else None)
            except Exception:
                closes = None
            if closes is None:
                continue
            q = compute_quote(closes)
            if q:
                quotes[t] = q
    return quotes


def main():
    micro = json.loads((DATA / "micro.json").read_text())
    records = micro.get("tickers", [])
    # skip names flagged as untradable / suspect quotes and obviously non-yfinance symbols
    tickers = [r["ticker"] for r in records
               if not r.get("quoteSuspect") and "(" not in r["ticker"]]

    print(f"Refreshing {len(tickers)} tickers via yfinance…")
    quotes = fetch_quotes(tickers)
    print(f"  got fresh quotes for {len(quotes)}/{len(tickers)}")

    refreshed = 0
    for r in records:
        r.pop("groupRank", None)                      # clear stale ranks before re-rank
        q = quotes.get(r["ticker"])
        if not q:
            continue                                  # keep last-known live fields
        r["price"] = q.get("price", r.get("price"))
        for k in ("vs50", "vs200", "range52w"):
            if q.get(k) is not None:
                r[k] = q[k]
        # recompute momentum sub-score from the fresh quote, then the composite
        mom = momentum_score({"vs50": r.get("vs50"), "vs200": r.get("vs200"),
                              "range52w": r.get("range52w"), "suspect": r.get("quoteSuspect")})
        subs = dict(r.get("subs") or {})
        if mom is not None:
            subs["momentum"] = round(mom, 1)
        if r.get("discovered"):
            # discovered names composite = mean(momentum, deep)*10 (mirrors micro_build)
            parts = [v for v in (subs.get("momentum"), subs.get("deep")) if v is not None]
            r["composite"] = round(sum(parts) / len(parts) * 10, 1) if parts else r.get("composite")
        else:
            comp, cov = composite_from_subs(subs)
            if comp is not None:
                r["composite"], r["coverage"] = comp, cov
        r["subs"] = subs
        refreshed += 1

    rank_within_groups(records)
    micro["updatedAt"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    micro["pricesRefreshedAt"] = micro["updatedAt"]
    (DATA / "micro.json").write_text(json.dumps(micro, indent=1))
    print(f"micro.json: refreshed prices/scores for {refreshed} names "
          f"({len(records) - refreshed} kept last-known)")


if __name__ == "__main__":
    main()
