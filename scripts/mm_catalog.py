#!/usr/bin/env python3
"""Snapshot the full MetalMiner catalogue our API token can see.

Reads:  METALMINER_API_TOKEN from the environment (a GitHub Actions secret; never
        written to disk or to git), or --from-file: a saved all_prices response,
        for testing. data/mm_series_registry.json, to mark which catalogue ids
        the daily mm_fetch.py pull already covers.
Writes: data/mm_catalog.json — metadata only, one entry per commodity_id
        (category, type, origin, description, unit, currency, price_future,
        lastDate). No price values, so nothing licensed lands in git.
        reports/mm_catalog.md — series per category with examples, then what the
        daily pull covers and which series look dead.

    METALMINER_API_TOKEN=... python3 scripts/mm_catalog.py
    python3 scripts/mm_catalog.py --from-file /tmp/all_prices_latest.json

Endpoint: GET {BASE}{path}/all_prices?token=...&format=json with no commodity_id
and no historical flag — per the API doc (Rev 3/23) that returns the latest row of
every series the token is entitled to. Tries the v2 route mm_fetch.py uses, then the
documented v1 route, and logs each response's shape (keys and lengths, never
values). Stdlib only. The token is never printed.
"""
import argparse
import collections
import datetime
import json
import os
import pathlib
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
REGISTRY = DATA / "mm_series_registry.json"
CATALOG = DATA / "mm_catalog.json"
REPORT = ROOT / "reports" / "mm_catalog.md"

BASE = "https://indx.metalminerindx.com"
# The route MetalMiner gave us on 2026-09-02, then the one in the Rev 3/23 doc.
PATHS = ("/api/commodities/2/all_prices", "/api/1/all_prices")
TIMEOUT = 180

META_FIELDS = ("category", "type", "origin", "description", "unit", "currency", "price_future")
EXAMPLES_PER_ROW = 6   # distinct types listed in a category's Examples cell
DEAD_DAYS = 90         # latest observation older than this = series looks discontinued


def fetch(token, path, opener=urllib.request.urlopen):
    q = urllib.parse.urlencode({"token": token, "format": "json"})
    req = urllib.request.Request(f"{BASE}{path}?{q}", headers={"Accept": "application/json"})
    try:
        with opener(req, timeout=TIMEOUT) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"_http_error": e.code, "_body": e.read().decode("utf-8", "replace")[:200]}
    except (urllib.error.URLError, TimeoutError, ValueError) as e:
        return {"_http_error": None, "_body": str(e)[:200]}


def describe(payload):
    """Shape of a response for the log — keys, lengths, error text; never price values."""
    if isinstance(payload, dict):
        if "_http_error" in payload:
            return f"HTTP {payload['_http_error']}: {payload['_body']}"
        parts = []
        for k, v in list(payload.items())[:8]:
            if isinstance(v, (list, dict)):
                parts.append(f"{k}: {type(v).__name__}[{len(v)}]")
            elif isinstance(v, str) and k.lower() in ("error", "message", "detail", "status"):
                parts.append(f"{k}: {v[:160]!r}")
            else:
                parts.append(f"{k}: {type(v).__name__}")
        return "dict {" + ", ".join(parts) + "}"
    if isinstance(payload, list):
        first = payload[0] if payload else None
        keys = list(first)[:12] if isinstance(first, dict) else type(first).__name__
        return f"list[{len(payload)}] first={keys}"
    return type(payload).__name__


def catalogue(payload):
    """Collapse an all_prices payload to {commodity_id: metadata}, keeping the newest row."""
    rows = payload
    if isinstance(payload, dict):
        rows = payload.get("commodities") or payload.get("data") or payload.get("results") or []
    out = {}
    for r in rows:
        if not isinstance(r, dict) or r.get("commodity_id") is None:
            continue
        cid = int(r["commodity_id"])
        date = str(r.get("collection_date") or r.get("date") or "")[:10]
        if cid in out and out[cid]["lastDate"] >= date:
            continue
        meta = {k: (str(r[k]).strip() if r.get(k) is not None else None) for k in META_FIELDS}
        meta["lastDate"] = date
        out[cid] = meta
    return out


def label(category):
    s = (category or "uncategorised").strip().replace("non ferrous", "non-ferrous")
    s = s[:1].upper() + s[1:]
    return s.replace("Mmi ", "MMI ")


def norm_type(t):
    # LME rows carry an " n" suffix ("aluminum n"); group them with the plain metal.
    return re.sub(r"\s+n$", "", (t or "?").strip())


def short_desc(d):
    # Drop dimensions like "(0.08 in x 48 in)" so "6061 t6 (...) sheet" reads "6061 t6 sheet".
    d = re.sub(r"\s+", " ", re.sub(r"\(.*?\)", "", d or "?")).strip()
    return d if len(d) <= 32 else d[:32].rsplit(" ", 1)[0] + "…"


def ranked(counter):
    return sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))


def fmt(name, n):
    return f"{name} ({n})" if n > 1 else name


def examples(series):
    """Most common types; when one type is most of the category (\"steel\" in Steel),
    break it down by product form instead so the cell says something."""
    types = ranked(collections.Counter(norm_type(m["type"]) for m in series))
    top, n_top = types[0]
    forms = ranked(collections.Counter(short_desc(m["description"]) for m in series
                                       if norm_type(m["type"]) == top))
    if n_top * 2 > len(series) and len(forms) > 1:
        head = f"{top} ({n_top}): " + ", ".join(fmt(d, n) for d, n in forms[:4])
        rest = [fmt(t, n) for t, n in types[1:3]]
        return "; ".join([head] + ([", ".join(rest)] if rest else []))
    return ", ".join(fmt(t, n) for t, n in types[:EXAMPLES_PER_ROW])


def single_example(m):
    origin = (m.get("origin") or "").lower()
    if origin and origin not in ("na", "global", "index"):
        return f"{norm_type(m['type'])} ({origin})"
    return norm_type(m["type"])


def age_days(date, today):
    try:
        return (today - datetime.date.fromisoformat(date)).days
    except (TypeError, ValueError):
        return None


def registry_ids():
    if not REGISTRY.exists():
        return set()
    return {int(r["id"]) for r in json.loads(REGISTRY.read_text())["series"]}


def render(cat, as_of, pulled):
    by_cat = collections.defaultdict(list)
    for cid, m in cat.items():
        by_cat[m["category"]].append((cid, m))
    multi = sorted(((c, s) for c, s in by_cat.items() if len(s) > 1), key=lambda cs: (-len(cs[1]), label(cs[0])))
    singles = sorted(((c, s) for c, s in by_cat.items() if len(s) == 1), key=lambda cs: label(cs[0]))

    lines = [
        "# MetalMiner catalogue",
        "",
        (f"Every series our API token can see, from the latest `all_prices` snapshot · as of {as_of} · "
         f"{len(cat)} series in {len(by_cat)} categories. Generated by `scripts/mm_catalog.py`; "
         "examples are the most common `type` values in each category, with series counts."),
        "",
        "| Category | Series | Examples |",
        "|---|---|---|",
    ]
    for c, s in multi:
        lines.append(f"| {label(c)} | {len(s)} | {examples([m for _, m in s])} |")
    if singles:
        names = [label(c) for c, _ in singles]
        names = [names[0]] + [n[:1].lower() + n[1:] if not n.startswith("MMI") else n for n in names[1:]]
        lines.append(f"| {', '.join(names)} | 1 each | {'; '.join(single_example(s[0][1]) for _, s in singles)} |")
    lines.append(f"| **Total** | **{len(cat)}** | |")

    today = datetime.date.fromisoformat(as_of)
    lines += [
        "",
        "## What our daily pull covers",
        "",
        (f"`mm_fetch.py` pulls the {len(pulled)} ids in `data/mm_series_registry.json` (+ its EXTRA_IDS). "
         f"**Dead** = latest observation more than {DEAD_DAYS} days before {as_of}."),
        "",
        "| Category | Series | Pulled | Not pulled | Dead |",
        "|---|---|---|---|---|",
    ]
    for c, s in sorted(by_cat.items(), key=lambda cs: (-len(cs[1]), label(cs[0]))):
        ids = [cid for cid, _ in s]
        n_pulled = sum(cid in pulled for cid in ids)
        dead = sum(1 for _, m in s if (age_days(m["lastDate"], today) or 0) > DEAD_DAYS)
        lines.append(f"| {label(c)} | {len(s)} | {n_pulled} | {len(s) - n_pulled} | {dead} |")
    n_pulled = sum(cid in pulled for cid in cat)
    lines.append(f"| **Total** | **{len(cat)}** | **{n_pulled}** | **{len(cat) - n_pulled}** | |")

    missing = sorted(pulled - set(cat))
    if missing:
        lines += ["", f"Registry ids absent from the catalogue snapshot ({len(missing)}): "
                  + ", ".join(map(str, missing)) + "."]
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--from-file", help="saved all_prices JSON response instead of calling the API")
    args = ap.parse_args()

    if args.from_file:
        cat = catalogue(json.loads(pathlib.Path(args.from_file).read_text()))
    else:
        token = os.environ.get("METALMINER_API_TOKEN", "").strip()
        if not token:
            print("mm_catalog: METALMINER_API_TOKEN not set — nothing pulled", file=sys.stderr)
            return 1
        cat = {}
        for path in PATHS:
            payload = fetch(token, path)
            cat = catalogue(payload)
            print(f"mm_catalog: {path} → {describe(payload)} → {len(cat)} series")
            if cat:
                break
    if not cat:
        print("mm_catalog: no route returned a series list — catalogue left untouched", file=sys.stderr)
        return 1
    now = datetime.datetime.now(datetime.timezone.utc)
    as_of = now.date().isoformat()

    CATALOG.write_text(json.dumps({
        "updatedAt": now.isoformat(timespec="seconds"),
        "asOf": as_of,
        "total": len(cat),
        "categories": dict(sorted(collections.Counter(m["category"] for m in cat.values()).items(),
                                  key=lambda kv: -kv[1])),
        "series": {str(k): cat[k] for k in sorted(cat)},
    }, indent=2) + "\n")
    REPORT.write_text(render(cat, as_of, registry_ids()))
    print(f"mm_catalog: {len(cat)} series → {CATALOG.relative_to(ROOT)}, {REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
