#!/usr/bin/env python3
"""Append a daily snapshot of each ranked name's micro scores to micro_history.jsonl.

Forward-looking only, same contract as exposure.py's position history: one append
per UTC day (guarded against the 4x/day refresh), one JSONL row per ranked ticker,
never backfilled. The accumulated history is what signal_ic.py later reads to measure
whether each sub-score actually predicted forward returns (rank-IC / IR) — so this
must run every day for the scorecard to have data. It is intentionally tiny (composite
+ sub-scores + a price anchor, not the whole 35-field record) to bound git growth.

Import record_snapshot() and call it from micro_refresh.py after micro.json is
rewritten, or run standalone against the current data/micro.json.
"""
import json
import pathlib

DATA = pathlib.Path(__file__).resolve().parent.parent / "data"


def record_snapshot(date=None):
    """Append today's ranked names + scores to micro_history.jsonl (once per day)."""
    micro = json.loads((DATA / "micro.json").read_text())
    records = micro.get("tickers", [])
    date = date or (micro.get("pricesRefreshedAt") or micro.get("updatedAt") or "")[:10]
    if not date:
        return

    history_path = DATA / "micro_history.jsonl"
    existing_dates = set()
    if history_path.exists():
        for line in history_path.read_text().splitlines():
            if line.strip():
                existing_dates.add(json.loads(line)["date"])
    if date in existing_dates:
        return  # already recorded today; refresh runs multiple times/day

    with history_path.open("a") as f:
        for r in records:
            composite = r.get("composite")
            price = r.get("price")
            if composite is None or price is None:
                continue  # a forward return needs a real price anchor
            subs = {k: v for k, v in (r.get("subs") or {}).items() if v is not None}
            hedge = ((r.get("hedgeFund") or {}).get("aggregate") or {}).get("signal")
            row = {
                "date": date,
                "ticker": r["ticker"],
                "composite": round(float(composite), 2),
                "subs": subs,
                "hedgeSignal": hedge,
                "priceAnchor": round(float(price), 4),
            }
            f.write(json.dumps(row) + "\n")


if __name__ == "__main__":
    record_snapshot()
    print("Recorded micro snapshot to data/micro_history.jsonl")
