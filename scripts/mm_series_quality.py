#!/usr/bin/env python3
"""Grade every series in a MetalMiner historical dump: tradable / level_only / rejected.

Reads a MetalMiner historical dump (`historical_<date>.json[.gz]`, licensed data — pass
its path on the command line, never commit it) and writes:

  reports/mm_series_quality.md     per-category table + defect lists (stale, frozen,
                                   holes, jumps) for a human reader
  data/mm_series_registry.json     {updatedAt, asOf, dumpDate, counts, series:[...]}
                                   — the machine-readable registry other scripts and
                                   verify_data.py consult before trusting a series

Why: the rare-earth cluster was scored off a MetalMiner MMI (a stepped composite index,
not a price) for months before anyone measured it. Any series can go stale, freeze into a
list price, or arrive as an index; this grades all of them on every dump so a bad proxy is
caught at ingestion rather than discovered downstream. Grades are conservative and the
thresholds are constants below — change them here, not per caller.

    python3 scripts/mm_series_quality.py /path/to/historical_20260818.json.gz
    python3 scripts/mm_series_quality.py dump.json.gz --asof 2026-08-18 --no-write

Stdlib only. Exit code is always 0: this is a grader, not a gate.
"""
import argparse
import datetime
import json
import math
import pathlib
import statistics
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from exposure import NON_PRICE_CATEGORIES  # noqa: E402  (composite indices, never prices)
from mmi_proxy_audit import load_dump  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
REPORT = ROOT / "reports" / "mm_series_quality.md"
REGISTRY = ROOT / "data" / "mm_series_registry.json"

# --- thresholds (measured against the 2026-08-18 dump; see reports/mm_series_quality.md)
STALE_DAYS = 30          # last observation older than this → rejected (series has stopped)
FROZEN_SHARE = 0.40      # consecutive-equal share above this → rejected (list price, not market)
FLAT_LEVEL_SHARE = 0.05  # 5–40% flat → level_only (usable for direction, not for returns)
JUMP_LOG = math.log(1.5)  # single-step |log move| above this counts as a suspicious jump
JUMP_MIN_OBS = 300       # a jump in a series shorter than this → rejected (unit/currency flip)
DAILY_MAX_GAP = 3        # median gap (days) above this → level_only (weekly/monthly cadence)
RECENT_YEARS = 3
RECENT_MIN_OBS = 600     # fewer observations in the last RECENT_YEARS → level_only
HOLE_DAYS = 120          # max gap above this in a daily series is reported as a hole
FLAT_RUN_REPORT = 60     # longest flat run above this is reported as frozen
PUBLIC_MARKERS = ("lme", "comex", "globex", "future", "cru")  # exchange-quoted → no edge


def series_stats(dates, values, asof):
    d = [datetime.date.fromisoformat(x) for x in dates]
    gaps = [(b - a).days for a, b in zip(d, d[1:])]
    flat_pairs = sum(1 for a, b in zip(values, values[1:]) if a == b)
    run = best = 0
    for a, b in zip(values, values[1:]):
        run = run + 1 if a == b else 0
        best = max(best, run)
    jumps = sum(1 for a, b in zip(values, values[1:])
                if a and b and a > 0 and b > 0 and abs(math.log(b / a)) > JUMP_LOG)
    recent_from = (asof - datetime.timedelta(days=365 * RECENT_YEARS)).isoformat()
    return {
        "obs": len(values),
        "start": dates[0],
        "end": dates[-1],
        "staleDays": (asof - d[-1]).days,
        "medianGapDays": statistics.median(gaps) if gaps else None,
        "maxGapDays": max(gaps) if gaps else None,
        "flatShare": round(flat_pairs / (len(values) - 1), 4) if len(values) > 1 else None,
        "longestFlatRun": best,
        "bigJumps": jumps,
        "recentObs": sum(1 for x in dates if x >= recent_from),
        "nonPositive": sum(1 for v in values if v is None or v <= 0),
    }


def grade(category, st):
    """Return (grade, reasons). Rejected beats level_only beats tradable."""
    rej, lvl = [], []
    if str(category).lower() in NON_PRICE_CATEGORIES:
        rej.append("composite index, not a price")
    if st["staleDays"] > STALE_DAYS:
        rej.append(f"stale {st['staleDays']}d (last {st['end']})")
    if st["flatShare"] is not None and st["flatShare"] > FROZEN_SHARE:
        rej.append(f"frozen: {st['flatShare']:.0%} of steps unchanged")
    if st["bigJumps"] and st["obs"] < JUMP_MIN_OBS:
        rej.append(f"{st['bigJumps']} >50% jump(s) in a {st['obs']}-obs series")
    if st["nonPositive"]:
        rej.append(f"{st['nonPositive']} non-positive value(s)")
    if rej:
        return "rejected", rej
    if st["medianGapDays"] is not None and st["medianGapDays"] > DAILY_MAX_GAP:
        lvl.append(f"cadence: median gap {st['medianGapDays']:.0f}d")
    if st["flatShare"] is not None and st["flatShare"] > FLAT_LEVEL_SHARE:
        lvl.append(f"{st['flatShare']:.0%} of steps unchanged")
    if st["recentObs"] < RECENT_MIN_OBS:
        lvl.append(f"only {st['recentObs']} obs in last {RECENT_YEARS}y")
    if st["bigJumps"]:
        lvl.append(f"{st['bigJumps']} >50% jump(s) — check before use")
    if lvl:
        return "level_only", lvl
    return "tradable", []


def build(series, meta, asof):
    rows = []
    for cid in sorted(series):
        dates = sorted(series[cid])
        values = [series[cid][d] for d in dates]
        st = series_stats(dates, values, asof)
        category = meta[cid]["category"]
        name = meta[cid]["label"]
        g, reasons = grade(category, st)
        rows.append({
            "id": cid, "category": category, "name": name, "grade": g,
            "unit": meta[cid]["unit"],
            "public": any(m in name.lower() for m in PUBLIC_MARKERS),
            "reasons": reasons, "stats": st,
        })
    counts = {}
    for r in rows:
        counts[r["grade"]] = counts.get(r["grade"], 0) + 1
    counts["tradable_public"] = sum(1 for r in rows if r["grade"] == "tradable" and r["public"])
    counts["tradable_proprietary"] = counts.get("tradable", 0) - counts["tradable_public"]
    return rows, counts


def render(rows, counts, asof, dump_name):
    by_cat = {}
    for r in rows:
        by_cat.setdefault(r["category"], []).append(r)
    L = ["# MetalMiner series quality", "",
         f"Source dump: `{dump_name}` · as of {asof} · {len(rows)} series.", "",
         "Grades: **tradable** = daily, fresh, not frozen, no suspicious jumps; "
         "**level_only** = usable for direction/level, not for return signals (weekly/monthly "
         "cadence, partly frozen, or thin recent history); **rejected** = composite index, "
         "stopped, frozen list price, or unit flip. `public` = exchange-quoted (LME/COMEX), "
         "so no information edge.", "",
         f"Counts: {json.dumps(counts)}", "",
         "| category | series | tradable (proprietary / public) | level_only | rejected |",
         "|---|---|---|---|---|"]
    for c, rs in sorted(by_cat.items()):
        t = [r for r in rs if r["grade"] == "tradable"]
        L.append(f"| {c} | {len(rs)} | {len(t)} ({sum(1 for r in t if not r['public'])} / "
                 f"{sum(1 for r in t if r['public'])}) | "
                 f"{sum(1 for r in rs if r['grade'] == 'level_only')} | "
                 f"{sum(1 for r in rs if r['grade'] == 'rejected')} |")

    def section(title, sel, cols):
        L.extend(["", f"## {title} ({len(sel)})", ""])
        if not sel:
            L.append("none")
            return
        L.append("| id | series | " + " | ".join(cols) + " |")
        L.append("|---|---|" + "---|" * len(cols))
        for r in sel:
            L.append(f"| {r['id']} | {r['name'][:70]} | " +
                     " | ".join(str(r["stats"][c]) for c in cols) + " |")

    st = lambda r: r["stats"]  # noqa: E731
    section("Stale: last observation > %dd before as-of" % STALE_DAYS,
            sorted([r for r in rows if st(r)["staleDays"] > STALE_DAYS], key=lambda r: -st(r)["staleDays"]),
            ["end", "staleDays", "obs"])
    section("Frozen: > %d%% unchanged steps or flat run > %d" % (FROZEN_SHARE * 100, FLAT_RUN_REPORT),
            sorted([r for r in rows if (st(r)["flatShare"] or 0) > FROZEN_SHARE
                    or st(r)["longestFlatRun"] > FLAT_RUN_REPORT], key=lambda r: -(st(r)["flatShare"] or 0)),
            ["flatShare", "longestFlatRun", "obs", "medianGapDays"])
    section("Holes: max gap > %dd in a daily/weekly series" % HOLE_DAYS,
            sorted([r for r in rows if (st(r)["maxGapDays"] or 0) > HOLE_DAYS
                    and (st(r)["medianGapDays"] or 99) <= 20], key=lambda r: -st(r)["maxGapDays"]),
            ["maxGapDays", "medianGapDays", "obs"])
    section("Jumps: single-step move > 50%",
            sorted([r for r in rows if st(r)["bigJumps"]], key=lambda r: -st(r)["bigJumps"]),
            ["bigJumps", "obs", "start", "end"])
    section("Tradable, proprietary (the series worth building signals on)",
            [r for r in rows if r["grade"] == "tradable" and not r["public"]],
            ["obs", "start", "recentObs", "staleDays"])
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("dump")
    ap.add_argument("--asof", help="YYYY-MM-DD; default = latest date in the dump")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()
    series, meta = load_dump(args.dump, structured=True)
    dump_date = max(max(s) for s in series.values())
    asof = datetime.date.fromisoformat(args.asof or dump_date)
    rows, counts = build(series, meta, asof)
    text = render(rows, counts, asof, pathlib.Path(args.dump).name)
    print(text)
    if args.no_write:
        return
    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text(text)
    REGISTRY.write_text(json.dumps({
        "updatedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "asOf": asof.isoformat(), "dumpDate": dump_date, "counts": counts, "series": rows,
    }, indent=2) + "\n")
    print(f"wrote {REPORT.relative_to(ROOT)} and {REGISTRY.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
