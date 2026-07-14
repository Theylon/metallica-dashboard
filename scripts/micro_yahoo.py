#!/usr/bin/env python3
"""Independent Yahoo Finance cross-validation pull for the Stock Picks tab.

The micro-analysis composite and the AI-Hedge-Fund layer are built from FMP /
TipRanks / TrueNorth data. This script pulls the SAME kinds of numbers (price,
analyst target + rating, margins/returns/leverage) from an INDEPENDENT source —
Yahoo Finance via `yfinance` — so the compiler can flag when the two disagree.
(Google Finance has no free/official API, so Yahoo is the practical second source;
`yfinance` is already a CI dependency.)

Output: data/micro_src/yahoo.json — a pure raw pull. All comparison logic lives in
`micro_build.py` so the cross-check is deterministic and testable. Missing / ADR-only
tickers Yahoo can't map are simply absent → the compiler degrades gracefully.

Run in the daily research Routine immediately before `micro_build.py`. It is NOT
needed in the 4x/day Action (that runs `micro_refresh.py`, which does not recompute
the cross-check).
"""
import datetime
import json
import os
import pathlib
import time

import yfinance as yf

DATA = pathlib.Path(__file__).resolve().parent.parent / "data"
SRC = pathlib.Path(os.environ.get("MICRO_SRC", str(DATA / "micro_src")))

# yf.Ticker(t).info key -> our normalized key. Kept explicit so the schema is stable.
FIELD_MAP = {
    "currentPrice": "price", "marketCap": "marketCap",
    "fiftyDayAverage": "fiftyDayAverage", "twoHundredDayAverage": "twoHundredDayAverage",
    "fiftyTwoWeekHigh": "fiftyTwoWeekHigh", "fiftyTwoWeekLow": "fiftyTwoWeekLow",
    "targetMeanPrice": "targetMean", "targetHighPrice": "targetHigh", "targetLowPrice": "targetLow",
    "numberOfAnalystOpinions": "numberOfAnalysts",
    "recommendationKey": "recommendationKey", "recommendationMean": "recommendationMean",
    "trailingPE": "trailingPE", "forwardPE": "forwardPE",
    "profitMargins": "profitMargins", "grossMargins": "grossMargins",
    "ebitdaMargins": "ebitdaMargins", "operatingMargins": "operatingMargins",
    "returnOnEquity": "returnOnEquity", "returnOnAssets": "returnOnAssets",
    "debtToEquity": "debtToEquity",
    "revenueGrowth": "revenueGrowth", "earningsGrowth": "earningsGrowth",
}


def ticker_list():
    """Names to cross-check: the scored universe, minus suspect/parenthetical symbols."""
    micro = DATA / "micro.json"
    if micro.exists():
        recs = json.loads(micro.read_text()).get("tickers", [])
    else:
        recs = json.loads((DATA / "universe.json").read_text())["tickers"]
        recs = [r for r in recs if not r.get("excluded")]
    return [r["ticker"] for r in recs
            if not r.get("quoteSuspect") and "(" not in r["ticker"]]


def pull_one(t):
    """Return the normalized field subset for one ticker, or None if Yahoo has nothing."""
    try:
        info = yf.Ticker(t).info or {}
    except Exception:
        return None
    price = info.get("currentPrice") or info.get("regularMarketPrice")
    if price is not None:
        info.setdefault("currentPrice", price)
    out = {}
    for src, dst in FIELD_MAP.items():
        v = info.get(src)
        if v is not None:
            out[dst] = v
    # need at least a price or an analyst target to be worth keeping
    return out if (out.get("price") is not None or out.get("targetMean") is not None) else None


def main():
    tickers = ticker_list()
    limit = int(os.environ.get("YAHOO_LIMIT", "0"))   # 0 = all; small value for quick tests
    if limit:
        tickers = tickers[:limit]
    print(f"Yahoo cross-validation: pulling {len(tickers)} tickers via yfinance…")

    quotes, ok, fail = {}, 0, 0
    for i, t in enumerate(tickers, 1):
        q = pull_one(t)
        if q:
            quotes[t] = q
            ok += 1
        else:
            fail += 1
        if i % 40 == 0:
            print(f"  {i}/{len(tickers)} ({ok} ok, {fail} missing)")
        time.sleep(0.15)   # be polite to Yahoo

    out = {
        "fetchedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "source": "yfinance (Yahoo Finance) — independent cross-validation layer",
        "quotes": quotes,
        "missing": fail,
    }
    (SRC / "yahoo.json").write_text(json.dumps(out, indent=1))
    print(f"yahoo.json: {ok} tickers with data ({fail} missing/unmapped)")


if __name__ == "__main__":
    main()
