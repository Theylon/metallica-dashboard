#!/usr/bin/env python3
"""Pull daily closes for the rare-earth equities into the JSON shape rare_earth_leadlag.py reads.

Reads:  Yahoo Finance via yfinance (works from the GitHub Action; Yahoo egress is
        blocked in Claude research sessions, where IBKR / TrueNorth pulls are used
        instead and saved by hand in the same shape).
Writes: --out (default /tmp/mm_equities.json): {"MP": {"YYYY-MM-DD": close, ...}, ...}
        Vendor price data — never committed.

    python3 scripts/mm_equities.py --tickers MP,REMX,LYSCF --start 2013-08-19

Best-effort: a ticker that fails is skipped with a message; exit 1 only if nothing
was fetched.
"""
import argparse
import json
import pathlib
import sys


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tickers", default="MP,REMX,LYSCF")
    ap.add_argument("--start", default="2013-08-19")
    ap.add_argument("--out", default="/tmp/mm_equities.json")
    args = ap.parse_args()
    try:
        import yfinance as yf
    except ImportError:
        print("mm_equities: yfinance not installed", file=sys.stderr)
        return 1
    out = {}
    for t in [x.strip() for x in args.tickers.split(",") if x.strip()]:
        try:
            h = yf.Ticker(t).history(start=args.start, auto_adjust=True)
            closes = {d.strftime("%Y-%m-%d"): round(float(c), 4) for d, c in h["Close"].items()
                      if c == c}  # drop NaN
            if closes:
                out[t] = closes
                print(f"mm_equities: {t} {len(closes)} closes {min(closes)}..{max(closes)}")
            else:
                print(f"mm_equities: {t} returned no rows", file=sys.stderr)
        except Exception as e:  # noqa: BLE001 — best-effort vendor pull
            print(f"mm_equities: {t} failed: {str(e)[:120]}", file=sys.stderr)
    if not out:
        return 1
    p = pathlib.Path(args.out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out))
    print(f"mm_equities: wrote {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
