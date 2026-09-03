#!/usr/bin/env python3
"""Pull MetalMiner price series from the MetalMiner API into a local dump file.

Reads:  METALMINER_API_TOKEN from the environment (a GitHub Actions secret in CI;
        never written to disk or to git). The commodity ids to pull come from
        data/mm_series_registry.json (every id graded so far) plus EXTRA_IDS
        (assessments MetalMiner opened to us after the 2026-08-18 dump).
Writes: --out (default /tmp/historical_latest.json.gz) in the same shape as a
        MetalMiner historical dump — {"commodities": [{collection_date,
        commodity_id, category, type, origin, description, unit, value}, ...]} —
        so mm_series_quality.py, mmi_proxy_audit.py and rare_earth_leadlag.py run
        on it unchanged. The dump is licensed data and stays OUT of git
        (.gitignore blocks historical_*.json[.gz]).
        data/mm_freshness.json — derived metadata only: per id, the last
        observation date and its lag in days behind the pull, plus counts. This
        answers "how stale is the Chinese assessment when we see it", which the
        rare-earth tests take as --delay.

    METALMINER_API_TOKEN=... python3 scripts/mm_fetch.py
    python3 scripts/mm_fetch.py --ids 270930,270581 --out /tmp/re.json.gz

Endpoint (per MetalMiner, 2026-09-02): GET {BASE}/api/commodities/2/all_prices
?token=...&commodity_id=<comma list>&historical=True&format=json. Refreshed
daily, early morning US Eastern. Stdlib only (urllib); ids are pulled in chunks so
one bad id cannot empty the whole dump. Exit 0 on a partial pull, 1 only when
nothing at all was fetched or the token is missing.
"""
import argparse
import datetime
import gzip
import json
import os
import pathlib
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
REGISTRY = DATA / "mm_series_registry.json"
FRESHNESS = DATA / "mm_freshness.json"

BASE = "https://indx.metalminerindx.com"
PATH = "/api/commodities/2/all_prices"
CHUNK = 20
TIMEOUT = 120

# Opened to our tier on 2026-09-02 (not in the 2026-08-18 dump): heavy rare earths
# and the FOB siblings of the Nd/Pr oxide series the Rare Earths MMI is built on.
EXTRA_IDS = [270581, 271055, 271053, 270908, 270924]

# The fields a dump row carries; anything else the API returns is dropped so the
# file stays byte-compatible with the historical dumps.
ROW_FIELDS = ("collection_date", "commodity_id", "category", "type", "origin",
              "description", "unit", "value")


def registry_ids():
    if not REGISTRY.exists():
        return []
    return [int(r["id"]) for r in json.loads(REGISTRY.read_text())["series"]]


def fetch_chunk(token, ids, opener=urllib.request.urlopen):
    q = urllib.parse.urlencode({"token": token, "commodity_id": ",".join(map(str, ids)),
                                "historical": "True", "format": "json"})
    req = urllib.request.Request(f"{BASE}{PATH}?{q}", headers={"Accept": "application/json"})
    with opener(req, timeout=TIMEOUT) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    return normalise(payload)


def normalise(payload):
    """Accept {"commodities": [...]}, a bare list, or {"data": [...]}; keep dump fields."""
    rows = payload
    if isinstance(payload, dict):
        rows = payload.get("commodities") or payload.get("data") or payload.get("results") or []
    out = []
    for r in rows:
        if not isinstance(r, dict) or r.get("commodity_id") is None:
            continue
        date = r.get("collection_date") or r.get("date")
        if not date:
            continue
        row = {k: r.get(k) for k in ROW_FIELDS}
        row["collection_date"] = str(date)[:10]
        row["commodity_id"] = int(r["commodity_id"])
        try:
            row["value"] = float(r.get("value") if r.get("value") is not None else r.get("price"))
        except (TypeError, ValueError):
            continue
        out.append(row)
    return out


def freshness(rows, pulled_at):
    last = {}
    for r in rows:
        cid = r["commodity_id"]
        if cid not in last or r["collection_date"] > last[cid]["lastDate"]:
            last[cid] = {"lastDate": r["collection_date"], "type": r.get("type"),
                         "category": r.get("category")}
    today = pulled_at.date()
    for cid, v in last.items():
        v["lagDays"] = (today - datetime.date.fromisoformat(v["lastDate"])).days
        v["obs"] = 0
    for r in rows:
        last[r["commodity_id"]]["obs"] += 1
    lags = sorted(v["lagDays"] for v in last.values())
    return {
        "updatedAt": pulled_at.isoformat(timespec="seconds"),
        "pulledAt": pulled_at.isoformat(timespec="seconds"),
        "seriesFetched": len(last), "rows": len(rows),
        "lagDaysMedian": lags[len(lags) // 2] if lags else None,
        "lagDaysMax": lags[-1] if lags else None,
        "series": {str(k): last[k] for k in sorted(last)},
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--ids", help="comma-separated commodity ids (default: registry + EXTRA_IDS)")
    ap.add_argument("--out", default="/tmp/historical_latest.json.gz")
    ap.add_argument("--no-freshness", action="store_true", help="do not write data/mm_freshness.json")
    args = ap.parse_args()

    token = os.environ.get("METALMINER_API_TOKEN", "").strip()
    if not token:
        print("mm_fetch: METALMINER_API_TOKEN not set — nothing pulled", file=sys.stderr)
        return 1
    ids = ([int(x) for x in args.ids.split(",") if x.strip()] if args.ids
           else sorted(set(registry_ids()) | set(EXTRA_IDS)))
    if not ids:
        print("mm_fetch: no ids to pull (registry missing?)", file=sys.stderr)
        return 1

    rows, failed = [], []
    for i in range(0, len(ids), CHUNK):
        chunk = ids[i:i + CHUNK]
        try:
            got = fetch_chunk(token, chunk)
            rows.extend(got)
            print(f"mm_fetch: ids {chunk[0]}..{chunk[-1]}: {len(got)} rows")
        except (urllib.error.URLError, urllib.error.HTTPError, ValueError, TimeoutError) as e:
            failed.append((chunk, str(e)[:120]))
            print(f"mm_fetch: ids {chunk[0]}..{chunk[-1]} FAILED: {str(e)[:120]}", file=sys.stderr)
    if not rows:
        print("mm_fetch: nothing fetched", file=sys.stderr)
        return 1

    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    opener = gzip.open if str(out).endswith(".gz") else open
    with opener(out, "wt", encoding="utf-8") as fh:
        json.dump({"commodities": rows}, fh)
    pulled_at = datetime.datetime.now(datetime.timezone.utc)
    print(f"mm_fetch: wrote {out} — {len(rows)} rows, {len({r['commodity_id'] for r in rows})} series, "
          f"{len(failed)} failed chunk(s)")
    if not args.no_freshness:
        doc = freshness(rows, pulled_at)
        doc["failedChunks"] = [{"ids": c, "error": e} for c, e in failed]
        FRESHNESS.write_text(json.dumps(doc, indent=2) + "\n")
        print(f"mm_fetch: wrote {FRESHNESS.relative_to(ROOT)} — median lag {doc['lagDaysMedian']}d, "
              f"max {doc['lagDaysMax']}d")
    return 0


if __name__ == "__main__":
    sys.exit(main())
