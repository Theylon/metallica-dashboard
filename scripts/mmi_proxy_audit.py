#!/usr/bin/env python3
"""Audit how well a MetalMiner MMI index tracks the real price assessments it is
used as a proxy for (the rare-earth cluster by default).

Reads a MetalMiner historical dump (`historical_<date>.json[.gz]`, a
`{"commodities": [{collection_date, commodity_id, category, type, ...}]}` list —
licensed data, keep it OUT of git; pass the path on the command line) and writes
reports/mmi_proxy_audit.md. Nothing under data/ is touched.

For the index and each assessment it reports raw observations, distinct weeks
observed, weekly-return volatility, the share of flat weeks, and the pairwise
weekly-return correlation matrix (last observation per ISO week, forward-filled
over the common window). Stdlib only.

    python3 scripts/mmi_proxy_audit.py /path/to/historical_20260818.json.gz
    python3 scripts/mmi_proxy_audit.py dump.json.gz --index 1474 --assess 270574,270575

The rare-earth defaults: index 1477 (rare earths mmi) against 270930 (PrNd oxide
exw), 270907 (Nd oxide exw), 270923 (Pr oxide exw), 270928 (PrNd mischmetal exw).
"""
import argparse
import datetime
import gzip
import json
import math
import pathlib
import statistics

ROOT = pathlib.Path(__file__).resolve().parent.parent
REPORT = ROOT / "reports" / "mmi_proxy_audit.md"

DEFAULT_INDEX = 1477
DEFAULT_ASSESS = [270930, 270907, 270923, 270928]


def load_dump(path, structured=False):
    """{commodity_id: {date: value}}, {commodity_id: label}.

    With structured=True the second dict holds {category, type, origin, description,
    unit, label} per id instead of the label string (mm_series_quality.py needs the
    category field on its own).
    """
    opener = gzip.open if str(path).endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8") as fh:
        rows = json.load(fh)["commodities"]
    series, meta = {}, {}
    for r in rows:
        cid = r["commodity_id"]
        series.setdefault(cid, {})[r["collection_date"]] = r["value"]
        label = f"{r['type']} ({r['category']}, {r['origin']}, {r['description']}, {r['unit']})"
        meta[cid] = ({"category": r["category"], "type": r["type"], "origin": r["origin"],
                      "description": r["description"], "unit": r["unit"], "label": label}
                     if structured else label)
    return series, meta


def weekly(s):
    """{(iso_year, iso_week): last value observed that week}."""
    out = {}
    for d, v in sorted(s.items()):
        y, w, _ = datetime.date.fromisoformat(d).isocalendar()
        out[(y, w)] = v
    return out


def log_returns(values):
    return [None if a in (None, 0) or b in (None, 0) else math.log(b / a)
            for a, b in zip(values, values[1:])]


def corr(a, b):
    pairs = [(x, y) for x, y in zip(a, b) if x is not None and y is not None]
    if len(pairs) < 3:
        return float("nan"), len(pairs)
    xs, ys = [p[0] for p in pairs], [p[1] for p in pairs]
    mx, my = statistics.mean(xs), statistics.mean(ys)
    sxy = sum((x - mx) * (y - my) for x, y in pairs)
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    return (sxy / math.sqrt(sxx * syy) if sxx and syy else float("nan")), len(pairs)


def audit(series, meta, index_id, assess_ids):
    ids = [index_id] + list(assess_ids)
    missing = [i for i in ids if i not in series]
    if missing:
        raise SystemExit(f"commodity ids not in dump: {missing}")
    start = max(min(series[i]) for i in ids)
    end = min(max(series[i]) for i in ids)
    wk = {i: weekly(series[i]) for i in ids}
    lo = datetime.date.fromisoformat(start).isocalendar()[:2]
    hi = datetime.date.fromisoformat(end).isocalendar()[:2]
    weeks = sorted(w for w in set().union(*wk.values()) if lo <= w <= hi)

    filled, stats = {}, {}
    for i in ids:
        last, vals = None, []
        for w in weeks:
            last = wk[i].get(w, last)
            vals.append(last)
        filled[i] = log_returns(vals)
        rets = [r for r in filled[i] if r is not None]
        stats[i] = {
            "rawObs": len(series[i]),
            "weeksObserved": sum(1 for w in weeks if w in wk[i]),
            "weeklyVol": statistics.pstdev(rets) if len(rets) > 1 else float("nan"),
            "flatWeeks": (sum(1 for r in rets if r == 0) / len(rets)) if rets else float("nan"),
        }
    matrix = {(a, b): corr(filled[a], filled[b]) for a in ids for b in ids if a < b}
    return {"window": (start, end), "weeks": len(weeks), "ids": ids,
            "stats": stats, "corr": matrix, "meta": {i: meta[i] for i in ids}}


def render(res, dump_name):
    ids, st = res["ids"], res["stats"]
    lines = [
        "# MMI proxy audit",
        "",
        f"Source dump: `{dump_name}` · window {res['window'][0]} → {res['window'][1]} "
        f"({res['weeks']} ISO weeks, last observation per week, forward-filled).",
        "",
        "| id | series | raw obs | weeks observed | weekly vol | flat weeks |",
        "|---|---|---|---|---|---|",
    ]
    for i in ids:
        s = st[i]
        lines.append(f"| {i} | {res['meta'][i]} | {s['rawObs']} | {s['weeksObserved']} | "
                     f"{s['weeklyVol']:.4f} | {s['flatWeeks']:.1%} |")
    lines += ["", "Weekly log-return correlation (n = overlapping weeks):", "",
              "| a | b | r | n |", "|---|---|---|---|"]
    for (a, b), (r, n) in res["corr"].items():
        lines.append(f"| {res['meta'][a].split(' (')[0]} | {res['meta'][b].split(' (')[0]} | {r:.2f} | {n} |")
    idx = ids[0]
    ref = ids[1]
    r_idx = [res["corr"][(min(idx, j), max(idx, j))][0] for j in ids[1:]]
    r_real = [r for (a, b), (r, _) in res["corr"].items() if idx not in (a, b)]
    lines += ["",
              f"Index vs assessments: r = {min(r_idx):.2f}–{max(r_idx):.2f}; "
              f"assessments among themselves: r = {min(r_real):.2f}–{max(r_real):.2f}. "
              f"Index weeks observed / reference: {st[idx]['weeksObserved']}/{st[ref]['weeksObserved']}; "
              f"index vol / reference vol: {st[idx]['weeklyVol'] / st[ref]['weeklyVol']:.2f}×.",
              ""]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("dump", help="MetalMiner historical dump (.json or .json.gz)")
    ap.add_argument("--index", type=int, default=DEFAULT_INDEX)
    ap.add_argument("--assess", default=",".join(map(str, DEFAULT_ASSESS)),
                    help="comma-separated assessment commodity ids")
    ap.add_argument("--no-write", action="store_true", help="print only")
    args = ap.parse_args()
    series, meta = load_dump(args.dump)
    res = audit(series, meta, args.index, [int(x) for x in args.assess.split(",") if x])
    text = render(res, pathlib.Path(args.dump).name)
    print(text)
    if not args.no_write:
        REPORT.parent.mkdir(exist_ok=True)
        REPORT.write_text(text + "\n")
        print(f"wrote {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
