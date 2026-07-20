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
import copy
import datetime
import json
import pathlib
import sys

import yfinance as yf

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from micro_score import momentum_score, composite_from_subs, rank_within_groups
from micro_build import cross_validation, load_held, live_macro_banner, live_sizing_note, _stamp_held_now

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


def fetch_quotes(tickers, series_out=None, keep=None):
    """Bulk-fetch 1y daily closes via yfinance, in chunks. Returns {ticker: quote}.

    If series_out is passed, also stash the raw 1y {dates, closes} for every ticker in
    `keep` (the held book) — the same download already in memory, so risk.py gets a
    per-name return series with no second network round-trip (see data/price_history.json).
    """
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
            if series_out is not None and (keep is None or t in keep):
                s = closes.dropna()
                if len(s) >= 2:
                    series_out[t] = {
                        "dates": [d.strftime("%Y-%m-%d") for d in s.index],
                        "closes": [round(float(x), 4) for x in s.values],
                    }
    return quotes


def held_nonotc():
    """Current held tickers, excluding OTC/@PINK and non-yfinance ('(') symbols."""
    try:
        positions = json.loads((DATA / "positions.json").read_text())["positions"]
    except Exception:
        return []
    return [p["ticker"] for p in positions
            if "@PINK" not in p["ticker"] and "(" not in p["ticker"]]


def write_price_history(series):
    """Write held-name close series to price_history.json (merge-and-keep on gaps)."""
    path = DATA / "price_history.json"
    existing = {}
    if path.exists():
        try:
            existing = json.loads(path.read_text()).get("tickers", {})
        except Exception:
            existing = {}
    existing.update({t: s for t, s in series.items() if s})  # refresh present, keep missing
    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    path.write_text(json.dumps({"updatedAt": now, "tickers": existing}, indent=1))
    print(f"price_history.json: {len(series)} held series refreshed, {len(existing)} total")


def main():
    micro = json.loads((DATA / "micro.json").read_text())
    prev_micro = copy.deepcopy(micro)   # pre-refresh state for the decision log diff
    records = micro.get("tickers", [])

    # Re-sync the held overlay from the live book on every refresh, so the
    # "Held" view can never drift from data/positions.json between full research
    # rebuilds (micro_build owns ADDING rows for brand-new held names; this
    # keeps the existing rows' held/heldMv/position truthful 4x/day).
    held_book = load_held()
    for r in records:
        h = held_book.get(r["ticker"])
        r["held"] = h["side"] if h else None
        r["heldMv"] = h["mktValue"] if h else None
        r["position"] = h
    # re-stamp the live-derived narrative fields so they never re-stale between
    # full research rebuilds: macro banner from macro.json, sizing note + the
    # recommendation/trade-list heldNow ground truth from the live book
    macro = live_macro_banner()
    if macro:
        micro["macro"] = macro
    sizing = live_sizing_note()
    if sizing:
        micro["sizingNote"] = sizing
    micro["recommendations"] = _stamp_held_now(micro.get("recommendations", []), held_book)
    micro["tradeList"] = _stamp_held_now(micro.get("tradeList", []), held_book)
    # skip names flagged as untradable / suspect quotes and obviously non-yfinance symbols
    tickers = [r["ticker"] for r in records
               if not r.get("quoteSuspect") and "(" not in r["ticker"]]

    # also fetch any held names not in the picks universe (e.g. ETF shorts) so the risk
    # engine's per-name return series (price_history.json) covers the whole book
    held = held_nonotc()
    held_set = set(held)
    fetch_list = list(dict.fromkeys(tickers + [h for h in held if h not in set(tickers)]))

    print(f"Refreshing {len(tickers)} tickers via yfinance ({len(fetch_list)} incl. held)…")
    series = {}
    quotes = fetch_quotes(fetch_list, series_out=series, keep=held_set)
    print(f"  got fresh quotes for {len(quotes)}/{len(fetch_list)}")
    write_price_history(series)

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

    # Refresh the Yahoo cross-check from the committed yahoo.json (no network here —
    # scripts/micro_yahoo.py produces it). crossVal is derived from each row's own
    # analyst/fundamentals/price vs the independent Yahoo pull. Only recompute when
    # yahoo.json has data, so a missing file never wipes a cross-check a full rebuild
    # already computed.
    yq = {}
    ypath = DATA / "micro_src" / "yahoo.json"
    if ypath.exists():
        yq = json.loads(ypath.read_text()).get("quotes", {})
    if yq:
        for r in records:
            try:
                r["crossVal"] = cross_validation(r.get("analyst"), r.get("fundamentals"),
                                                 r.get("price"), yq.get(r["ticker"]))
            except Exception:
                pass  # one odd record must never abort the whole price refresh

    micro["updatedAt"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    micro["pricesRefreshedAt"] = micro["updatedAt"]

    # record recommendation/held changes + their triggers before overwriting
    try:
        import decision_log
        decision_log.log_diff(prev_micro, micro, "micro_refresh")
    except Exception as e:
        print(f"decision log skipped: {e}")

    (DATA / "micro.json").write_text(json.dumps(micro, indent=1))
    print(f"micro.json: refreshed prices/scores for {refreshed} names "
          f"({len(records) - refreshed} kept last-known), "
          f"cross-val from {len(yq)} Yahoo quotes")

    # append today's scores to micro_history.jsonl (once/day) for the signal scorecard
    try:
        import micro_snapshot
        micro_snapshot.record_snapshot()
    except Exception as e:
        print(f"micro snapshot skipped: {e}")


if __name__ == "__main__":
    main()
