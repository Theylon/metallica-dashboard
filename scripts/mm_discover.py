#!/usr/bin/env python3
"""Probe the MetalMiner API for which commodity ids are open to our tier.

Reads:  METALMINER_API_TOKEN from the environment (GitHub Actions secret; never
        written anywhere). data/mm_series_registry.json, to flag ids we already grade.
Writes: a markdown table to stdout (and to $GITHUB_STEP_SUMMARY when set) — one
        row per id that returned data: category, type, origin, description,
        unit, first/last date, observation count. Metadata only: no prices are
        printed or saved, so nothing licensed leaves the runner.

MetalMiner has no catalog endpoint we know of, only all_prices by id, and ids
are allocated roughly alphabetically within a block (270768 lanthanum oxide,
270787 lithium carbonate, 270789 lithium hydroxide, 270800 lutetium oxide). So
discovering what else exists means asking for the ids around the ones we know.

    METALMINER_API_TOKEN=... python3 scripts/mm_discover.py
    python3 scripts/mm_discover.py --ranges 270769-270799,72080-72110
"""
import argparse
import json
import os
import pathlib
import sys
import urllib.error

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from mm_fetch import CHUNK, REGISTRY, fetch_chunk  # noqa: E402

# Lithium sits between lanthanum (270768) and lutetium (270800); the battery
# cathode indices are 72092-72098; the "northeast asia" block (229555 erbium ..
# 229605 yttrium) may carry its own lithium assessments.
DEFAULT_RANGES = "72080-72110,270769-270799,229550-229610"

ERRORS = (urllib.error.URLError, urllib.error.HTTPError, ValueError, TimeoutError)


def parse_ranges(spec):
    ids = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        lo, _, hi = part.partition("-")
        ids.update(range(int(lo), int(hi or lo) + 1))
    return sorted(ids)


def probe(token, ids):
    """Rows for every id that returns data. A failed chunk is retried id by id so
    one refused id cannot hide its neighbours."""
    rows, refused = [], []
    for i in range(0, len(ids), CHUNK):
        chunk = ids[i:i + CHUNK]
        try:
            rows.extend(fetch_chunk(token, chunk))
            continue
        except ERRORS:
            pass
        for cid in chunk:
            try:
                rows.extend(fetch_chunk(token, [cid]))
            except ERRORS as e:
                refused.append((cid, str(e)[:80]))
    return rows, refused


def summarise(rows):
    meta = {}
    for r in rows:
        m = meta.setdefault(r["commodity_id"], {k: r.get(k) for k in
                                                ("category", "type", "origin", "description", "unit")}
                            | {"first": r["collection_date"], "last": r["collection_date"], "obs": 0})
        m["first"] = min(m["first"], r["collection_date"])
        m["last"] = max(m["last"], r["collection_date"])
        m["obs"] += 1
    return meta


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--ranges", default=DEFAULT_RANGES, help="comma-separated id ranges, e.g. 270769-270799")
    args = ap.parse_args()

    token = os.environ.get("METALMINER_API_TOKEN", "").strip()
    if not token:
        print("mm_discover: METALMINER_API_TOKEN not set — nothing probed", file=sys.stderr)
        return 1
    ids = parse_ranges(args.ranges)
    known = set()
    if REGISTRY.exists():
        known = {int(s["id"]) for s in json.loads(REGISTRY.read_text())["series"]}

    rows, refused = probe(token, ids)
    meta = summarise(rows)

    lines = [f"## MetalMiner id probe — {args.ranges}",
             f"{len(ids)} ids asked, {len(meta)} returned data "
             f"({len([c for c in meta if c not in known])} not yet in the registry), {len(refused)} refused.",
             "",
             "| id | status | category | type | origin | description | unit | first | last | obs |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for cid in sorted(meta):
        m = meta[cid]
        lines.append(f"| {cid} | {'known' if cid in known else 'NEW'} | {m['category']} | {m['type']} | "
                     f"{m['origin']} | {m['description']} | {m['unit']} | {m['first']} | {m['last']} | {m['obs']} |")
    if refused:
        lines += ["", "Refused: " + ", ".join(f"{c} ({e})" for c, e in refused)]
    text = "\n".join(lines) + "\n"
    print(text)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as fh:
            fh.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
