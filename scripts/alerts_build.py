#!/usr/bin/env python3
"""Build data/alerts.json — process-rule alerts for the dashboard.

Two rule families (the hard rules live in PROCESS.md):

  earnings_proximity — a HELD name reports within ALERT_DAYS. The process rule
    is to close/reduce before earnings (binary event, elevated volatility) —
    regardless of how good the alt-data looks. severity: warn ≤7d, info ≤14d.
    Earnings dates come from altdata.json (kpi.earningsDate) and events.json;
    the earliest known date wins.

  micro_override — a recent decision-log entry (≤14d) flagged microOverride
    (micro recommendation contradicts the commodity/macro bias) on a name still
    held. Overrides are allowed but must stay visible until resolved.

Surfaced on the Process tab and as an Overview banner. Stdlib only, reads only
committed data/ files → runs in the GitHub Action.
"""
import datetime
import json
import pathlib

DATA = pathlib.Path(__file__).resolve().parent.parent / "data"
ALERT_DAYS = 14
WARN_DAYS = 7
OVERRIDE_LOOKBACK_DAYS = 14


def _load(name, default):
    p = DATA / name
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text())
    except Exception:
        return default


def _base(t):
    return (t or "").split(" @")[0].upper()


def earnings_dates():
    """ticker → earliest known earnings date (ISO), from altdata + events."""
    dates = {}

    def put(ticker, d):
        if not ticker or not d:
            return
        d = str(d)[:10]
        try:
            datetime.date.fromisoformat(d)
        except ValueError:
            return
        t = _base(ticker)
        if t not in dates or d < dates[t]:
            dates[t] = d

    for it in _load("altdata.json", {}).get("items", []):
        put(it.get("ticker"), (it.get("kpi") or {}).get("earningsDate"))
    for it in _load("events.json", {}).get("items", []):
        put(it.get("ticker"), it.get("nextEarnings") or it.get("earningsDate"))
    return dates


def earnings_alerts(positions, today):
    dates = earnings_dates()
    items = []
    for p in positions:
        t = _base(p.get("ticker"))
        d = dates.get(t)
        if not d:
            continue
        days = (datetime.date.fromisoformat(d) - today).days
        if not (0 <= days <= ALERT_DAYS):
            continue
        items.append({
            "type": "earnings_proximity",
            "ticker": t,
            "earningsDate": d,
            "daysToEarnings": days,
            "held": p.get("side"),
            "heldMv": p.get("mktValue"),
            "severity": "warn" if days <= WARN_DAYS else "info",
            "rule": "Close or reduce positions before earnings (elevated volatility)",
            "message": f"{t} reports in {days} day{'s' if days != 1 else ''} ({d}) — "
                       f"process rule: close/reduce before earnings",
        })
    items.sort(key=lambda a: a["daysToEarnings"])
    return items


def override_alerts(positions, today):
    path = DATA / "decision_log.jsonl"
    if not path.exists():
        return []
    held = {_base(p.get("ticker")) for p in positions}
    cutoff = (today - datetime.timedelta(days=OVERRIDE_LOOKBACK_DAYS)).isoformat()
    latest = {}   # one alert per ticker — keep the newest override entry
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        try:
            e = json.loads(line)
        except Exception:
            continue
        t = _base(e.get("ticker"))
        if (e.get("microOverride") and t in held and (e.get("ts") or "") >= cutoff):
            latest[t] = e
    items = []
    for t, e in sorted(latest.items()):
        bias = (e.get("macroContext") or {}).get("bias")
        material = (e.get("macroContext") or {}).get("material")
        held_side = (e.get("snapshot") or {}).get("held")
        items.append({
            "type": "micro_override",
            "ticker": t,
            "severity": "info",
            "rule": "Micro override of the macro bias must stay visible until resolved",
            "message": f"{t}: micro call \"{e.get('action')}\" (held {held_side or '—'}) "
                       f"contradicts the {bias or '?'} {material or ''} bias "
                       f"(decision logged {(e.get('ts') or '')[:10]})".replace("  ", " "),
        })
    return items


def build():
    positions = _load("positions.json", {"positions": []}).get("positions", [])
    today = datetime.datetime.now(datetime.timezone.utc).date()
    items = earnings_alerts(positions, today) + override_alerts(positions, today)
    return {
        "updatedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "items": items,
    }


if __name__ == "__main__":
    doc = build()
    (DATA / "alerts.json").write_text(json.dumps(doc, indent=1) + "\n")
    warns = sum(1 for a in doc["items"] if a["severity"] == "warn")
    print(f"alerts.json: {len(doc['items'])} alerts ({warns} warn)")
