#!/usr/bin/env python3
"""Deduplicate PLS adverse-event news into stories and events.

Reads (never writes):
  research/pls_adverse_events/stories_raw.json   every story the Bigdata.com
                                                 searches returned, one row per
                                                 document, timestamps verbatim
  research/pls_adverse_events/event_merges.json  manual map {alias_key: canonical_key}
                                                 for the same event filed under two
                                                 keys; also lists rejected keys
Writes:
  research/pls_adverse_events/stories.json       unique stories (duplicates removed)
  research/pls_adverse_events/events.json        one row per event, with the UTC
                                                 timestamp of its first report and the
                                                 timestamps of every story about it

Duplicate stories, removed in this order:
  1. the same document id returned by more than one search;
  2. syndicated copies: the same normalised headline within SYNDICATION_DAYS
     (the earliest copy is kept; the others are listed under `copies`).
Timestamps are never altered; the earliest one per event becomes
`first_report_utc`. Consumed by scripts/adverse_event_block.py. Stdlib only.
"""
from __future__ import annotations

import datetime as dt
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
RES = ROOT / "research" / "pls_adverse_events"
SYNDICATION_DAYS = 3
CATEGORIES = ["production_cut", "cost_increase", "outage", "funding_problem"]


def norm_headline(h: str) -> str:
    h = (h or "").lower()
    h = re.sub(r"\s[-|–]\s[^-|–]{2,40}$", "", h)       # trailing " - Source Name"
    h = re.sub(r"^(update\s*\d*:|\*)\s*", "", h)
    return re.sub(r"[^a-z0-9]+", " ", h).strip()


def ts(s):
    if not s:
        return None
    t = dt.datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    return t if t.tzinfo else t.replace(tzinfo=dt.timezone.utc)


def main() -> int:
    raw = json.loads((RES / "stories_raw.json").read_text())
    merges_doc = json.loads((RES / "event_merges.json").read_text())
    merges = merges_doc.get("merges", {})
    rejected = set(merges_doc.get("rejected", {}))
    overrides = merges_doc.get("overrides", {})

    # 1) exact duplicates by document id
    by_id, n_idDup = {}, 0
    for s in raw:
        k = s.get("doc_id") or f"{s.get('source')}|{s.get('headline')}|{s.get('timestamp')}"
        if k in by_id:
            n_idDup += 1
            continue
        by_id[k] = s
    stories = sorted(by_id.values(), key=lambda s: (ts(s.get("timestamp")) or dt.datetime.max.replace(tzinfo=dt.timezone.utc)))

    # canonical event key; drop rejected events
    for s in stories:
        k = s.get("event_key")
        while k in merges:
            k = merges[k]
        s["event_key"] = k
    n_rej = sum(s["event_key"] in rejected for s in stories)
    stories = [s for s in stories if s["event_key"] not in rejected]

    # 2) syndicated copies: same normalised headline within SYNDICATION_DAYS
    kept, n_synd = [], 0
    for s in stories:
        h, t = norm_headline(s.get("headline")), ts(s.get("timestamp"))
        twin = next((k for k in kept if norm_headline(k.get("headline")) == h and h
                     and t and ts(k.get("timestamp"))
                     and abs((t - ts(k["timestamp"])).total_seconds()) <= SYNDICATION_DAYS * 86400), None)
        if twin:
            twin.setdefault("copies", []).append(
                {"doc_id": s.get("doc_id"), "source": s.get("source"), "timestamp": s.get("timestamp")})
            n_synd += 1
            continue
        kept.append(s)

    # 3) events
    events = {}
    for s in kept:
        e = events.setdefault(s["event_key"], {"event_id": s["event_key"], "stories": []})
        e["stories"].append(s)
    out_events = []
    for k, e in events.items():
        ss = sorted(e["stories"], key=lambda s: ts(s.get("timestamp")) or dt.datetime.max.replace(tzinfo=dt.timezone.utc))
        first = ss[0]
        # the event's label comes from its most severe story (ties: company disclosure first)
        lead = max(ss, key=lambda s: ((s.get("severity") or 0), bool(s.get("is_company_disclosure"))))
        row = {
            "event_id": k,
            "category": lead.get("category"),
            "subtype": lead.get("subtype"),
            "asset": lead.get("asset"),
            "severity": max((s.get("severity") or 0) for s in ss),
            "summary": lead.get("summary"),
            "first_report_utc": first.get("timestamp"),
            "first_report_source": first.get("source"),
            "first_report_headline": first.get("headline"),
            "first_is_company_disclosure": bool(first.get("is_company_disclosure")),
            "n_stories": len(ss),
            "stories": [{"doc_id": s.get("doc_id"), "timestamp": s.get("timestamp"),
                         "source": s.get("source"), "headline": s.get("headline")} for s in ss],
        }
        row.update(overrides.get(k, {}))
        out_events.append(row)
    out_events.sort(key=lambda e: (ts(e["first_report_utc"]) or dt.datetime.max.replace(tzinfo=dt.timezone.utc)))

    meta = {
        "source": "Bigdata.com search (entity 9561FC, fast and smart modes), PLS Group Ltd / Pilbara Minerals",
        "newsWindow": "2020-12-01 to 2026-09-23",
        "categories": CATEGORIES,
        "dedupe": {"rawStories": len(raw), "duplicateDocIds": n_idDup,
                   "rejectedEventStories": n_rej, "syndicatedCopies": n_synd},
        "nStories": len(kept),
        "nEvents": len(out_events),
        "generatedAt": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
    }
    (RES / "stories.json").write_text(json.dumps({**meta, "stories": kept}, indent=2, ensure_ascii=False))
    (RES / "events.json").write_text(json.dumps({**meta, "events": out_events}, indent=2, ensure_ascii=False))
    print(f"raw {len(raw)} → id-dupes {n_idDup}, rejected {n_rej}, syndicated {n_synd} "
          f"→ {len(kept)} stories, {len(out_events)} events")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
