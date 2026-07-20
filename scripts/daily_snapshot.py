#!/usr/bin/env python3
"""Daily full-data snapshot — record EVERY live data point for later analysis.

The live data/*.json files are overwritten in place on every refresh, so analyst
recommendations, sentiment, fundamentals, insider/politician cards, KPI nowcasts,
scores etc. lose their history the moment they change. This script freezes the
entire content of every live/derived file, verbatim, into one gzipped JSON per
UTC day:

    history/daily/YYYY-MM-DD.json.gz
    { "date": "...", "capturedAt": "...", "files": { "<name>": <full parsed JSON>, ... } }

Called on every refresh (Action 4x/day + mcp_refresh.py), it REWRITES today's
file each time so the day's snapshot converges to end-of-day state; past days
are never touched. Lives outside data/ on purpose — the Pages deploy ships
data/ wholesale and the archive must not bloat the public site.

Not captured: static inputs (report.json, universe.json, linkage_map.json),
price_history.json (large + reconstructible from yfinance), micro_src/, and the
append-only *.jsonl streams (micro_history, positioning_history,
position_history, orders, decision_log) — those already keep their own history
in full.

Review/analysis CLI:
    --list                          available snapshots + sizes
    --show DATE [FILE]              print one captured file (or the key list)
    --series TICKER DOTTED.FIELD    CSV time series of a micro-ticker field
                                    across all snapshots, e.g.
                                    --series TSLA analyst.priceTarget
                                    --series CLF subs.momentum

Stdlib only -> runs in the GitHub Action.
"""
import datetime
import gzip
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DEST = ROOT / "history" / "daily"

# every live/derived file the dashboard reads — the full parsed JSON is embedded
CAPTURE = [
    "account.json", "positions.json", "pnl.json", "benchmarks.json",
    "micro.json", "rebalance.json", "altdata.json",
    "analysts.json", "commodities.json", "macro.json", "macro_history.json",
    "metals_spot.json", "news.json", "technicals.json", "research.json",
    "events.json", "positioning.json", "journal.json",
    "risk.json", "exposure_history.json", "signal_scorecard.json",
    "channel_accuracy.json", "alerts.json",
]


def _load(name):
    p = DATA / name
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except Exception as e:
        print(f"  ! skip {name}: {e}")
        return None


# Keep a bounded window of daily snapshots. gzipped blobs don't delta-compress
# in git, so each rewrite stores a near-full new object; without a cap the repo
# grows ~170 MB/yr. A rolling quarter is plenty for the review helpers below.
RETAIN_DAYS = 90


def _prune(keep=RETAIN_DAYS):
    """Delete the oldest daily snapshots beyond the retention window."""
    snaps = sorted(DEST.glob("*.json.gz"))
    for p in snaps[:-keep] if keep and len(snaps) > keep else []:
        try:
            p.unlink()
            print(f"history/daily: pruned {p.name} (beyond {keep}-day window)")
        except OSError:
            pass


def record(date=None):
    """Write (or rewrite) today's snapshot. Returns the path."""
    now = datetime.datetime.now(datetime.timezone.utc)
    date = date or now.date().isoformat()
    files = {}
    for name in CAPTURE:
        doc = _load(name)
        if doc is not None:
            files[name.rsplit(".", 1)[0]] = doc
    snap = {"date": date, "capturedAt": now.isoformat(timespec="seconds"), "files": files}
    DEST.mkdir(parents=True, exist_ok=True)
    path = DEST / f"{date}.json.gz"
    with gzip.open(path, "wt", encoding="utf-8") as f:
        json.dump(snap, f, separators=(",", ":"))
    print(f"history/daily/{path.name}: {len(files)}/{len(CAPTURE)} files, "
          f"{path.stat().st_size // 1024} KB gz")
    _prune()
    return path


# ── review helpers ───────────────────────────────────────────────────────────
def _read(path):
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def list_snapshots():
    for p in sorted(DEST.glob("*.json.gz")):
        print(f"{p.name[:10]}  {p.stat().st_size // 1024:>5} KB")


def show(date, name=None):
    snap = _read(DEST / f"{date}.json.gz")
    if not name:
        print(f"captured {snap['capturedAt']} — files: {', '.join(sorted(snap['files']))}")
        return
    doc = snap["files"].get(name)
    if doc is None:
        sys.exit(f"'{name}' not in that snapshot (have: {', '.join(sorted(snap['files']))})")
    json.dump(doc, sys.stdout, indent=1)
    print()


def _dig(obj, dotted):
    for part in dotted.split("."):
        if not isinstance(obj, dict):
            return None
        obj = obj.get(part)
    return obj


def series(ticker, dotted):
    """CSV of one micro-ticker field across all snapshots (date,value)."""
    print(f"date,{dotted}")
    for p in sorted(DEST.glob("*.json.gz")):
        snap = _read(p)
        for r in (snap["files"].get("micro") or {}).get("tickers", []):
            if r.get("ticker") == ticker:
                v = _dig(r, dotted)
                print(f"{snap['date']},{'' if v is None else v}")
                break


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        record()
    elif args[0] == "--list":
        list_snapshots()
    elif args[0] == "--show" and len(args) >= 2:
        show(args[1], args[2] if len(args) > 2 else None)
    elif args[0] == "--series" and len(args) == 3:
        series(args[1].upper(), args[2])
    else:
        sys.exit(__doc__)
