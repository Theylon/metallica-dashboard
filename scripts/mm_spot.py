#!/usr/bin/env python3
"""Build the dashboard's metal price panel (data/metals_spot.json) from a MetalMiner dump.

Reads:  a MetalMiner dump in the historical shape — the file scripts/mm_fetch.py pulls
        from the API each run (default /tmp/historical_latest.json.gz; licensed data,
        never committed) — plus data/mm_series_registry.json for each series' grade.
Writes: data/metals_spot.json — {updatedAt, source, items: [...]}, one item per
        series in SPOT: the latest observation only (name, market, group, price,
        currency, unit, asOf, lagDays, changePct vs the previous observation,
        change1mPct vs ~30 days earlier, trend, id, grade). No history is written, so
        the committed file carries a handful of latest prints, never the licensed series.

Why: the panel used to be filled from MetalMiner MCP dumps by enrich.py, a path no
routine runs any more — it froze on 2026-07-17. The API pull already lands every
series in the Action daily, so the panel is now derived from it.

Rules: a series the registry grades "rejected" (frozen, stale, composite index, unit
flip) is skipped, never shown as a price. A series missing from this dump keeps its
last-good item from the existing file; a missing or empty dump leaves the file
untouched (degrade, don't blank).

    python3 scripts/mm_spot.py /tmp/historical_latest.json.gz
    python3 scripts/mm_spot.py dump.json.gz --out /tmp/metals_spot.json

Stdlib only. Exit 0 unless the dump is unreadable.
"""
import argparse
import datetime
import gzip
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
REGISTRY = DATA / "mm_series_registry.json"
OUT = DATA / "metals_spot.json"

# (commodity_id, display name, market, group, currency). Currency is only filled
# where the market prices in USD by definition (LME, COMEX, US assessments); a
# currency the API reports on the row wins over this, and an unknown one stays None
# rather than guessed. Ids and names are from data/mm_series_registry.json.
SPOT = [
    (1416, "Copper", "LME cash", "Base", "USD"),
    (295, "Aluminum", "LME cash", "Base", "USD"),
    (1270, "Nickel", "LME cash", "Base", "USD"),
    (972, "Zinc", "LME cash", "Base", "USD"),
    (678, "Tin", "LME cash", "Base", "USD"),
    (318, "Lead", "LME cash", "Base", "USD"),
    (9933, "Gold", "COMEX spot", "Precious", "USD"),
    (9938, "Silver", "COMEX spot", "Precious", "USD"),
    (187, "Platinum", "US sponge", "Precious", "USD"),
    (184, "Palladium", "US sponge", "Precious", "USD"),
    (82099, "HRC", "US CRU spot", "Steel", "USD"),
    (258, "HRC", "China", "Steel", None),
    (33075, "HRC", "Europe", "Steel", None),
    (153, "Shredded scrap #2", "US", "Steel", "USD"),
    (270787, "Lithium carbonate", "America FOB", "Battery", None),
    (270789, "Lithium hydroxide", "China", "Battery", None),
    (270557, "Cobalt sulfate", "China", "Battery", None),
    (270914, "Nickel sulfate", "China", "Battery", None),
    (270930, "PrNd oxide", "China EXW", "Rare earths", None),
    (270581, "Dysprosium oxide", "China FOB", "Rare earths", None),
    (271055, "Terbium oxide", "China FOB", "Rare earths", None),
]

TREND_PCT = 2.0      # |1M change| below this reads "flat"
MONTH_DAYS = 30


def load(path):
    """{id: {date: value}}, {id: {unit, currency}} from a dump (rows as mm_fetch writes them)."""
    opener = gzip.open if str(path).endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8") as fh:
        rows = json.load(fh)["commodities"]
    series, meta = {}, {}
    for r in rows:
        try:
            cid, date, val = int(r["commodity_id"]), str(r["collection_date"])[:10], float(r["value"])
        except (KeyError, TypeError, ValueError):
            continue
        series.setdefault(cid, {})[date] = val
        m = meta.setdefault(cid, {})
        if r.get("unit"):
            m["unit"] = r["unit"]
        if r.get("currency"):
            m["currency"] = str(r["currency"]).upper()
    return series, meta


def pct(new, old):
    return round((new / old - 1) * 100, 2) if old else None


def item(cid, name, market, group, currency, obs, meta, grade, today):
    dates = sorted(obs)
    last = dates[-1]
    price = obs[last]
    prev = obs[dates[-2]] if len(dates) > 1 else None
    cutoff = (datetime.date.fromisoformat(last) - datetime.timedelta(days=MONTH_DAYS)).isoformat()
    month_ago = [d for d in dates if d <= cutoff]
    chg_1m = pct(price, obs[month_ago[-1]]) if month_ago else None
    trend = ("" if chg_1m is None else "up" if chg_1m >= TREND_PCT
             else "down" if chg_1m <= -TREND_PCT else "flat")
    return {
        "name": name, "market": market, "group": group,
        "price": round(price, 2),
        "currency": meta.get("currency") or currency,
        "unit": meta.get("unit", ""),
        "asOf": last,
        "lagDays": (today - datetime.date.fromisoformat(last)).days,
        "changePct": pct(price, prev),
        "change1mPct": chg_1m,
        "trend": trend,
        "id": cid, "grade": grade,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("dump", nargs="?", default="/tmp/historical_latest.json.gz")
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()

    dump = pathlib.Path(args.dump)
    if not dump.exists():
        print(f"mm_spot: {dump} not found — metals_spot.json left as is", file=sys.stderr)
        return 0
    try:
        series, meta = load(dump)
    except (OSError, ValueError, KeyError, TypeError) as e:
        print(f"mm_spot: cannot read {dump}: {e}", file=sys.stderr)
        return 1

    grades = {}
    if REGISTRY.exists():
        grades = {int(r["id"]): r.get("grade") for r in json.loads(REGISTRY.read_text())["series"]}
    out = pathlib.Path(args.out)
    previous = {}
    if out.exists():
        try:
            previous = {i["id"]: i for i in json.loads(out.read_text()).get("items", []) if "id" in i}
        except (ValueError, AttributeError):
            pass

    now = datetime.datetime.now(datetime.timezone.utc)
    items, fresh, kept, skipped = [], 0, [], []
    for cid, name, market, group, currency in SPOT:
        grade = grades.get(cid)
        if grade == "rejected":
            skipped.append(cid)
            continue
        if series.get(cid):
            items.append(item(cid, name, market, group, currency, series[cid], meta.get(cid, {}),
                              grade, now.date()))
            fresh += 1
        elif cid in previous:
            old = dict(previous[cid])
            old["lagDays"] = (now.date() - datetime.date.fromisoformat(old["asOf"])).days
            items.append(old)
            kept.append(cid)

    if not fresh:
        print("mm_spot: none of the panel's series are in this dump — metals_spot.json left as is",
              file=sys.stderr)
        return 0
    doc = {"updatedAt": now.isoformat(timespec="seconds"), "source": "metalminer-api",
           "items": items}
    out.write_text(json.dumps(doc, indent=2) + "\n")
    print(f"mm_spot: wrote {out} — {fresh} fresh, kept last-good: {kept or 'none'}, "
          f"skipped as rejected: {skipped or 'none'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
