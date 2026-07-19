#!/usr/bin/env python3
"""Decision & trigger log — the "why" behind every recommendation change.

Append-only data/decision_log.jsonl. Every time a rebuild/refresh changes a
name's recommendation (action/urgency) or its held side, one JSONL row records
the trigger that moved: which sub-scores shifted, composite from→to, the price
snapshot, the commodity-bias context, and whether the micro call contradicts
the macro bias (microOverride) — so the process can be audited later ("was the
trigger right?") instead of reconstructed from memory.

Two entry points:
  log_diff(prev_micro, new_micro, source) — called from micro_build.py /
    micro_refresh.py with the pre-overwrite micro.json dict and the dict about
    to be written. Non-fatal by contract: callers wrap it in try/except.
  --update-outcomes CLI — backfills outcome.d30/.d90 (forward price return
    from data/micro_history.jsonl anchors) once entries age past 30/90 days,
    closing the loop for process review. Only the outcome object of an
    existing line is ever mutated; nothing else is rewritten.

Stdlib only → runs in the GitHub Action.
"""
import datetime
import json
import os
import pathlib
import sys

DATA = pathlib.Path(__file__).resolve().parent.parent / "data"
LOG = DATA / "decision_log.jsonl"

MAX_MOVERS = 3          # largest sub-score deltas recorded per entry
OUTCOME_DAYS = (30, 90)  # forward review horizons (calendar days)

# action classes that assert a directional bet vs. ones that only de-risk
_MAINTAIN = {"KEEP", "ADD", "HOLD", "NEW", "BUY", "OPEN", "INCREASE", "SWAP"}
_DERISK = {"COVER", "EXIT", "CLOSE", "TRIM", "REDUCE", "SELL"}


def action_class(action):
    """Normalized first token of the free-text action ('TRIM 1/3 PRE-EARNINGS' → 'TRIM')."""
    if not action:
        return None
    for tok in str(action).upper().replace("/", " ").split():
        if tok.isalpha():
            return tok
    return None


def _rec_direction(action, held):
    """The directional bet a recommendation asserts, or None for pure de-risking."""
    a = (action or "").upper()
    cls = action_class(a)
    if cls in _DERISK:
        return None
    if "LONG" in a:
        return "long"
    if "SHORT" in a:
        return "short"
    if held in ("long", "short") and cls in _MAINTAIN:
        return held
    return None


def _micro_override(action, held, bias):
    """True when the micro recommendation contradicts the material's macro bias."""
    d = _rec_direction(action, held)
    return bool(d and bias in ("long", "short") and d != bias)


def _rec_maps(micro):
    """ticker → {action, urgency, rationale, held} from tickers[] (recommendations[] fallback)."""
    out = {}
    for r in micro.get("recommendations") or []:
        t = r.get("ticker")
        if t:
            out[t] = {"action": r.get("action"), "urgency": r.get("urgency"),
                      "held": r.get("held")}
    for r in micro.get("tickers") or []:
        rec = r.get("recommendation")
        if rec and rec.get("action"):
            out[r["ticker"]] = {"action": rec.get("action"), "urgency": rec.get("urgency"),
                                "held": r.get("held")}
    return out


def _ticker_map(micro):
    return {r["ticker"]: r for r in micro.get("tickers") or [] if r.get("ticker")}


def _bias_for(micro, material):
    for b in micro.get("commodityBias") or []:
        if b.get("material") == material:
            return {"material": b.get("material"), "bias": b.get("bias"), "score": b.get("score")}
    return None


def _movers(prev_rec, new_rec):
    """Up to MAX_MOVERS largest sub-score deltas + composite from→to."""
    ps = (prev_rec or {}).get("subs") or {}
    ns = (new_rec or {}).get("subs") or {}
    deltas = []
    for k in set(ps) | set(ns):
        a, b = ps.get(k), ns.get(k)
        if a is not None and b is not None and a != b:
            deltas.append({"field": "subs." + k, "from": a, "to": b})
    deltas.sort(key=lambda d: -abs(d["to"] - d["from"]))
    return {
        "movers": deltas[:MAX_MOVERS],
        "compositeFrom": (prev_rec or {}).get("composite"),
        "compositeTo": (new_rec or {}).get("composite"),
    }


def _existing_keys_today(day):
    """Dedupe guard: {(ticker, event, action, prevAction)} already logged this UTC day."""
    keys = set()
    if not LOG.exists():
        return keys
    for line in LOG.read_text().splitlines():
        if not line.strip():
            continue
        try:
            e = json.loads(line)
        except Exception:
            continue
        if (e.get("ts") or "")[:10] == day:
            keys.add((e.get("ticker"), e.get("event"), e.get("action"), e.get("prevAction")))
    return keys


def log_diff(prev_micro, new_micro, source):
    """Diff two micro.json dicts and append one entry per changed decision."""
    prev_micro, new_micro = prev_micro or {}, new_micro or {}
    prev_recs, new_recs = _rec_maps(prev_micro), _rec_maps(new_micro)
    prev_tk, new_tk = _ticker_map(prev_micro), _ticker_map(new_micro)

    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    seen = _existing_keys_today(now[:10])
    entries = []

    def add(ticker, event, action, prev_action, urgency, prev_urgency):
        key = (ticker, event, action, prev_action)
        if key in seen:
            return
        seen.add(key)
        nr, pr = new_tk.get(ticker) or {}, prev_tk.get(ticker) or {}
        held = nr.get("held") if nr else (new_recs.get(ticker) or {}).get("held")
        bias = _bias_for(new_micro, nr.get("material")) if nr else None
        entries.append({
            "ts": now,
            "ticker": ticker,
            "event": event,
            "action": action,
            "actionClass": action_class(action),
            "urgency": urgency,
            "prevAction": prev_action,
            "prevUrgency": prev_urgency,
            "trigger": _movers(pr, nr),
            "snapshot": {
                "composite": nr.get("composite"),
                "subs": {k: v for k, v in (nr.get("subs") or {}).items() if v is not None},
                "price": nr.get("price"),
                "held": held,
            },
            "macroContext": bias,
            "microOverride": _micro_override(action, held, (bias or {}).get("bias")),
            "source": source,
            "outcome": {"d30": None, "d90": None, "checkedAt": None},
        })

    # recommendation appeared / changed / retired
    for t in sorted(set(prev_recs) | set(new_recs)):
        p, n = prev_recs.get(t), new_recs.get(t)
        if p and n and (p.get("action") != n.get("action") or p.get("urgency") != n.get("urgency")):
            add(t, "recommendation_change", n.get("action"), p.get("action"),
                n.get("urgency"), p.get("urgency"))
        elif n and not p:
            add(t, "recommendation_change", n.get("action"), None, n.get("urgency"), None)
        elif p and not n:
            add(t, "recommendation_change", None, p.get("action"), None, p.get("urgency"))

    # held side opened / closed / flipped (an executed decision)
    for t in sorted(set(prev_tk) | set(new_tk)):
        ph = (prev_tk.get(t) or {}).get("held")
        nh = (new_tk.get(t) or {}).get("held")
        if ph != nh and t in prev_tk and t in new_tk:
            add(t, "position_change", nh, ph, None, None)

    if entries:
        with LOG.open("a") as f:
            for e in entries:
                f.write(json.dumps(e) + "\n")
        print(f"decision_log.jsonl: +{len(entries)} entries ({source})")
    return entries


# ── outcome backfill ─────────────────────────────────────────────────────────
def _history_by_date():
    path = DATA / "micro_history.jsonl"
    if not path.exists():
        return {}
    by_date = {}
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        by_date.setdefault(r["date"], {})[r["ticker"]] = r.get("priceAnchor")
    return by_date


def _forward_price(by_date, dates, ticker, start, days):
    """First anchor for ticker on/after start+days (within a 10-day grace window)."""
    target = start + datetime.timedelta(days=days)
    for d in dates:
        dd = datetime.date.fromisoformat(d)
        if dd >= target:
            if dd > target + datetime.timedelta(days=10):
                return None   # history has a hole — don't fake an outcome
            return by_date[d].get(ticker)
    return None


def update_outcomes():
    """Fill outcome.d30/.d90 (raw forward price return, %) on aged entries."""
    if not LOG.exists():
        print("decision_log.jsonl: nothing to update")
        return 0
    by_date = _history_by_date()
    dates = sorted(by_date)
    today = datetime.datetime.now(datetime.timezone.utc).date()
    lines, updated = [], 0
    for line in LOG.read_text().splitlines():
        if not line.strip():
            continue
        try:
            e = json.loads(line)
        except Exception:
            lines.append(line)
            continue
        try:
            start = datetime.date.fromisoformat((e.get("ts") or "")[:10])
            anchor = (e.get("snapshot") or {}).get("price")
        except Exception:
            start, anchor = None, None
        changed = False
        if start and anchor:
            for days in OUTCOME_DAYS:
                key = f"d{days}"
                if e.get("outcome", {}).get(key) is None and (today - start).days >= days:
                    fwd = _forward_price(by_date, dates, e.get("ticker"), start, days)
                    if fwd:
                        e.setdefault("outcome", {})[key] = round((fwd / anchor - 1) * 100, 2)
                        changed = True
        if changed:
            e["outcome"]["checkedAt"] = today.isoformat()
            updated += 1
        lines.append(json.dumps(e))
    if updated:
        tmp = LOG.with_suffix(".jsonl.tmp")
        tmp.write_text("\n".join(lines) + "\n")
        os.replace(tmp, LOG)
    print(f"decision_log.jsonl: outcomes updated on {updated} entries")
    return updated


if __name__ == "__main__":
    if "--update-outcomes" in sys.argv:
        update_outcomes()
    else:
        print("Usage: decision_log.py --update-outcomes "
              "(log_diff is called from micro_build.py / micro_refresh.py)")
