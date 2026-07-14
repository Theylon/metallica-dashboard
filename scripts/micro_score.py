#!/usr/bin/env python3
"""Shared scoring primitives for the micro-analysis pipeline.

Single source of truth for the price/composite math so the two entry points can't
drift: the full MCP builder (`micro_build.py`, run in a Claude session) and the
free daily price refresh (`micro_refresh.py`, run in the GitHub Action).

The composite reads as "attractiveness as a LONG" (0-100); a low score on a liquid
name is a short candidate. Missing sub-scores redistribute their weight.
"""

WEIGHTS = {
    "momentum": 0.18, "commodity": 0.18, "deep": 0.14, "analyst": 0.13,
    "fundamentals": 0.12, "sentiment": 0.09, "smart": 0.08, "quality": 0.08,
}


def clamp(v, lo=0.0, hi=10.0):
    return max(lo, min(hi, v))


def momentum_score(q):
    """0-10 from price vs 50/200DMA and position in the 52-week range.

    q: {vs50, vs200, range52w, suspect}. Returns None for suspect/absent quotes.
    """
    if not q or q.get("suspect"):
        return None
    s = 5.0
    if q.get("vs50") is not None:
        s += clamp(q["vs50"] / 6.0, -2.5, 2.5)      # ±15% vs 50DMA saturates
    if q.get("vs200") is not None:
        s += clamp(q["vs200"] / 12.0, -2.5, 2.5)    # ±30% vs 200DMA saturates
    if q.get("range52w") is not None:
        s += (q["range52w"] - 50.0) / 25.0          # 52w-range position, ±2
    return clamp(s)


def composite_from_subs(subs):
    """Weighted 0-100 composite from a {sub_name: 0-10 or None} dict.

    Missing sub-scores drop out and their weight is redistributed across the rest.
    Returns (composite or None, coverage_pct 0-100).
    """
    avail = {k: v for k, v in (subs or {}).items() if v is not None and k in WEIGHTS}
    if not avail:
        return None, 0
    wsum = sum(WEIGHTS[k] for k in avail)
    composite = sum(WEIGHTS[k] * v for k, v in avail.items()) / wsum * 10.0
    coverage = round(wsum / sum(WEIGHTS.values()) * 100)
    return round(composite, 1), coverage


def rank_within_groups(records):
    """Assign r['groupRank'] = 'i/n' within each material group.

    Only tradable names with a composite are ranked (mirrors micro_build.py); other
    names are left without a groupRank key. Callers that re-rank refreshed scores
    should `r.pop('groupRank', None)` on every record first so stale ranks clear.
    """
    by_mat = {}
    for r in records:
        if r.get("composite") is not None and r.get("tradable"):
            by_mat.setdefault(r.get("material"), []).append(r)
    for rows in by_mat.values():
        rows.sort(key=lambda r: -r["composite"])
        for i, r in enumerate(rows, 1):
            r["groupRank"] = f"{i}/{len(rows)}"
