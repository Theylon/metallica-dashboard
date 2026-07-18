#!/usr/bin/env python3
"""
altdata_build.py — compiler for the Alt-Data tab.

Reads committed inputs in data/altdata_src/ and writes data/altdata.json:

  1. data/positions.json          -> the metals "book" group (held names)
  2. data/altdata_src/watchlist.json -> the consumer/TMT "watchlist" group + book driver map
  3. data/altdata_src/alt_r*.json -> research shards (narratives, trends, KPI nowcast, track record)

Design (matches the rest of the repo): pure Python, additive & resilient. Every
book/watchlist name gets an auto-generated default item so the tab is never empty;
research shards overlay those by ticker. A missing/malformed input is skipped, not
fatal. Never touches report.json / benchmarks.json.

The porting of the M Science *method* (KPI nowcast vs consensus + track record +
drill-down drivers + narrative) lives in the item shape below — fed by our OWN
MCP/web data, not by any third-party proprietary report text.
"""
import json, glob, os, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
SRC = os.path.join(DATA, "altdata_src")


def load(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        print(f"  ! skip {os.path.basename(path)}: {e}")
        return default


def clean_ticker(t):
    return (t or "").split(" @")[0].strip().upper()


def default_item(ticker, group, name, sector, extra):
    item = {
        "ticker": ticker, "group": group, "name": name, "sector": sector,
        "signal": "neutral", "conviction": "low",
        "asOf": None,
        "narrative": "",
        "drivers": [], "trend": None,
        "kpi": None, "trackRecord": [], "sources": [],
    }
    item.update(extra)
    return item


def build():
    watch_cfg = load(os.path.join(SRC, "watchlist.json"), {})
    book_drivers = watch_cfg.get("bookDrivers", {})
    watchlist = watch_cfg.get("watchlist", [])

    items = {}   # ticker -> item

    # 1. Book group from live positions
    pos = load(os.path.join(DATA, "positions.json"), {"positions": []})
    for p in pos.get("positions", []):
        tkr = clean_ticker(p.get("ticker"))
        if not tkr:
            continue
        cat = p.get("category") or "Other"
        side = p.get("side") or ""
        drv = book_drivers.get(cat, book_drivers.get("Other", {}))
        drivers = []
        if drv.get("series"):
            drivers.append({"dim": "Commodity", "label": drv.get("metal", cat),
                            "note": f"Driver series: {drv['series']}"})
        if side:
            drivers.append({"dim": "Position", "label": f"Held {side}", "note": f"{cat} exposure"})
        items[tkr] = default_item(
            tkr, "book", tkr, cat,
            {"narrative": f"Awaiting alt-data refresh. Metals-mosaic driver: "
                          f"{drv.get('series', 'per-name commodity exposure')}.",
             "drivers": drivers})

    # 2. Watchlist group (consumer / TMT) from config
    for w in watchlist:
        tkr = clean_ticker(w.get("ticker"))
        if not tkr:
            continue
        items[tkr] = default_item(
            tkr, "watchlist", w.get("name", tkr), w.get("sector", ""),
            {"narrative": f"Awaiting alt-data refresh — KPI tracked: {w.get('kpi', '?')} "
                          f"({w.get('unit', '')}) via {w.get('altProxy', 'alt-data proxies')}.",
             "kpi": {"name": w.get("kpi"), "unit": w.get("unit"), "ourEst": None,
                     "consensus": None, "deltaPct": None, "yoyPct": None, "earningsDate": None}})

    # 3. Overlay research shards (alt_r*.json), sorted so higher-numbered shards win
    shard_count = 0
    for path in sorted(glob.glob(os.path.join(SRC, "alt_r*.json"))):
        shard = load(path, {})
        for it in shard.get("items", []):
            tkr = clean_ticker(it.get("ticker"))
            if not tkr:
                continue
            base = items.get(tkr, default_item(tkr, it.get("group", "watchlist"),
                                               it.get("name", tkr), it.get("sector", ""), {}))
            base.update({k: v for k, v in it.items() if not k.startswith("_")})
            items[tkr] = base
            shard_count += 1

    # 4. Order: book first then watchlist; richer cards (with trend/kpi/track record) first
    def richness(it):
        return (bool(it.get("trend")) + bool((it.get("kpi") or {}).get("consensus") is not None)
                + bool(it.get("trackRecord")))

    ordered = sorted(
        items.values(),
        key=lambda it: (0 if it["group"] == "book" else 1, -richness(it), it["ticker"]))

    out = {
        "updatedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "counts": {
            "book": sum(1 for i in ordered if i["group"] == "book"),
            "watchlist": sum(1 for i in ordered if i["group"] == "watchlist"),
            "researched": sum(1 for i in ordered if richness(i) > 0),
        },
        "items": ordered,
    }
    dest = os.path.join(DATA, "altdata.json")
    with open(dest, "w") as f:
        json.dump(out, f, indent=2)
    print(f"  wrote {dest}: {out['counts']} ({shard_count} shard overlays)")


if __name__ == "__main__":
    print("Building data/altdata.json …")
    build()
