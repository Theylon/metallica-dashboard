#!/usr/bin/env python3
"""Order audit log — append-only record of every IBKR order instruction.

Companion to trade_gate.py: after the gate clears and the owner confirms, the
session creates the IBKR order instruction and records it here; when the owner
submits/cancels it in IBKR (or it fills), the status is updated in place. The
result is a complete audit trail of what was ordered, why, what the gate said,
and what became of it — data/orders.jsonl, append-only, one JSON object per
line. The dashboard's Orders tab renders it read-only; validate_data.py
enforces per-line parseability (a bad line blanks the tab) and
verify_data.check_process_files() adds warn-only semantic checks.

Usage:
  append (after create_order_instruction):
    python3 scripts/order_log.py --append --ticker SGML --side BUY --qty 10 \
        --order-type LIMIT --limit 10.25 --tif DAY --conid 511477158 \
        --instruction-id 1234 --url https://... \
        --trigger-source recommendation --trigger-ref "COVER, urgency high" \
        --reason "thesis conflict with bullish steel" \
        --gates "size_order:WARN" --note "owner confirmed in session"
  update (after submission/cancel/fill):
    python3 scripts/order_log.py --set-status --instruction-id 1234 --status submitted \
        [--fill-price 46.16]
  backfill trade outcomes (forward price returns on filled orders):
    python3 scripts/order_log.py --update-outcomes
  show recent:
    python3 scripts/order_log.py --list [-n 10]

Statuses: created → submitted → filled | cancelled | expired.

Outcomes (the look-back loop, mirroring decision_log.py's d30/d90): every
`filled` order gets `outcome.d1/.d5/.d30` — the raw forward price return (%)
from its fill price (fallback: limit price), anchored on daily prices in
data/micro_history.jsonl. The Orders tab colors them by whether the move
confirmed the trade's side (a BUY wants the price up — true both for opening a
long and for covering a short before a catalyst; a SELL wants it down). Short
horizons on purpose: these are catalyst trades (earnings, tariff decisions), so
"was the trigger right?" is usually answerable within days.
Stdlib only.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import pathlib
import sys

LOG = pathlib.Path(__file__).resolve().parent.parent / "data" / "orders.jsonl"
HISTORY = LOG.parent / "micro_history.jsonl"
STATUSES = ["created", "submitted", "filled", "cancelled", "expired"]
# an order past one of these is done — its instructionId may be safely recycled
TERMINAL = {"filled", "cancelled", "expired"}
# forward-return horizons for filled orders; short because these are catalyst trades
OUTCOME_DAYS = (1, 5, 30)


def _now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def append(a) -> int:
    entry = {
        "ts": _now(),
        "ticker": a.ticker.upper(),
        "side": a.side,
        "qty": a.qty,
        "orderType": a.order_type,
        "limit": a.limit,
        "tif": a.tif,
        "conid": a.conid,
        "instructionId": a.instruction_id,
        "url": a.url,
        "status": a.status or "created",
        "statusUpdatedAt": _now(),
        # what prompted the ticket — the execution-side analog of the decision
        # log's trigger, so the later review can ask "was the trigger right?"
        "trigger": {"source": a.trigger_source, "ref": a.trigger_ref or None},
        "reason": a.reason or None,    # the owner's why, verbatim
        "gates": a.gates or None,      # e.g. "size_order:WARN,earnings_window:FAIL-overridden"
        "note": a.note or None,        # operational context / follow-ups
    }
    # Warn if this instructionId is being reused while a prior order with the
    # same id is still OPEN — set_status can no longer target that prior order
    # unambiguously (see the NUE/CLF "101" collision). Terminal ids recycle fine.
    if a.instruction_id and LOG.exists():
        for line in LOG.read_text().splitlines():
            try:
                e = json.loads(line)
            except Exception:
                continue
            if (str(e.get("instructionId")) == str(a.instruction_id)
                    and e.get("status") not in TERMINAL):
                print(f"WARN: instructionId {a.instruction_id} is already used by an OPEN "
                      f"{e.get('ticker')} order ({e.get('status')}, {e.get('ts')}). Reusing it "
                      f"means --set-status can't target that order by id alone — close it first "
                      f"or use --ts to disambiguate.")
                break
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"orders.jsonl: +1 {entry['side']} {entry['qty']:g} {entry['ticker']} "
          f"({entry['status']}, instruction {entry['instructionId'] or '—'})")
    return 0


def set_status(a) -> int:
    if not LOG.exists():
        print("orders.jsonl: no log yet")
        return 1
    lines, hit = [], None
    for line in LOG.read_text().splitlines():
        if not line.strip():
            continue
        try:
            e = json.loads(line)
        except Exception:
            lines.append(line)
            continue
        lines.append(e)
    # Resolve which entry to transition. instructionIds can collide (recycled
    # across days, or reused while a prior order is still open), so prefer the
    # newest OPEN match — an already-terminal order shouldn't be re-transitioned
    # ahead of a live one. --ts picks a specific entry when even that is ambiguous.
    matches = [x for x in lines if isinstance(x, dict)
               and str(x.get("instructionId")) == str(a.instruction_id)]
    if a.ts:
        matches = [x for x in matches if str(x.get("ts", "")).startswith(a.ts)]
    if not matches:
        print(f"orders.jsonl: no entry with instructionId {a.instruction_id}"
              + (f" and ts starting {a.ts}" if a.ts else ""))
        return 1
    open_matches = [x for x in matches if x.get("status") not in TERMINAL]
    pool = open_matches or matches
    hit = pool[-1]   # newest (append order preserved)
    if len(pool) > 1:
        others = [f"{x.get('ticker')}/{x.get('status')}/{x.get('ts')}" for x in pool[:-1]]
        print(f"WARN: instructionId {a.instruction_id} matches {len(pool)} orders "
              f"({'open' if open_matches else 'all-terminal'}); updating the newest "
              f"({hit.get('ticker')}/{hit.get('ts')}). Others: {', '.join(others)}. "
              f"Use --ts to target a specific one.")
    hit["status"] = a.status
    hit["statusUpdatedAt"] = _now()
    if a.fill_price is not None:
        hit["fillPrice"] = a.fill_price
    if a.note:
        hit["note"] = (str(hit.get("note")) + " | " if hit.get("note") else "") + a.note
    tmp = LOG.with_suffix(".jsonl.tmp")
    tmp.write_text("\n".join(
        json.dumps(x) if isinstance(x, dict) else x for x in lines) + "\n")
    os.replace(tmp, LOG)
    print(f"orders.jsonl: instruction {a.instruction_id} → {a.status}")
    return 0


def _history_by_date():
    """{date: {ticker: priceAnchor}} from micro_history.jsonl (same as decision_log)."""
    if not HISTORY.exists():
        return {}
    by_date = {}
    for line in HISTORY.read_text().splitlines():
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


def update_outcomes() -> int:
    """Fill outcome.d1/.d5/.d30 (raw forward price return, %) on filled orders."""
    if not LOG.exists():
        print("orders.jsonl: no log yet")
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
        anchor = e.get("fillPrice") or e.get("limit")
        try:
            start = datetime.date.fromisoformat((e.get("ts") or "")[:10])
        except Exception:
            start = None
        changed = False
        if e.get("status") == "filled" and start and anchor:
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
    print(f"orders.jsonl: outcomes updated on {updated} entries")
    return 0


def list_tail(a) -> int:
    if not LOG.exists():
        print("orders.jsonl: no log yet")
        return 0
    rows = []
    for line in LOG.read_text().splitlines():
        try:
            rows.append(json.loads(line))
        except Exception:
            continue
    for e in rows[-a.n:]:
        trig = e.get("trigger") or {}
        print(f"{e.get('ts', '?')}  {e.get('status', '?'):9}  "
              f"{e.get('side', '?')} {e.get('qty', '?')} {e.get('ticker', '?')} "
              f"@ {e.get('limit') if e.get('limit') is not None else 'MKT'} "
              f"({e.get('tif', '?')})  instr={e.get('instructionId') or '—'}"
              + (f"  [{trig.get('source')}]" if trig.get("source") else "")
              + (f"  reason={e['reason']}" if e.get("reason") else "")
              + (f"  note={e['note']}" if e.get("note") else ""))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Append-only order audit log.")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--append", action="store_true")
    mode.add_argument("--set-status", action="store_true")
    mode.add_argument("--update-outcomes", action="store_true")
    mode.add_argument("--list", action="store_true")
    ap.add_argument("--ticker")
    ap.add_argument("--side", choices=["BUY", "SELL"])
    ap.add_argument("--qty", type=float)
    ap.add_argument("--order-type", choices=["LIMIT", "MARKET"])
    ap.add_argument("--limit", type=float, default=None)
    ap.add_argument("--fill-price", type=float, default=None,
                    help="with --set-status: actual execution price (outcome anchor)")
    ap.add_argument("--tif", default="DAY")
    ap.add_argument("--conid", type=int, default=None)
    ap.add_argument("--instruction-id", default=None)
    ap.add_argument("--ts", default=None,
                    help="with --set-status: ts prefix to disambiguate a reused instructionId")
    ap.add_argument("--url", default=None)
    ap.add_argument("--status", choices=STATUSES, default=None)
    ap.add_argument("--trigger-source", default="owner",
                    choices=["owner", "recommendation", "rebalance", "alert"])
    ap.add_argument("--trigger-ref", default=None,
                    help="compact snapshot of the triggering row, e.g. 'COVER, urgency high, composite 38'")
    ap.add_argument("--reason", default=None, help="the owner's rationale, verbatim")
    ap.add_argument("--gates", default=None)
    ap.add_argument("--note", default=None)
    ap.add_argument("-n", type=int, default=10)
    a = ap.parse_args()

    if a.append:
        missing = [k for k in ("ticker", "side", "qty", "order_type")
                   if getattr(a, k) is None]
        if missing:
            print(f"ERR: --append needs {', '.join('--' + m.replace('_', '-') for m in missing)}")
            return 2
        return append(a)
    if a.set_status:
        if not a.instruction_id or not a.status:
            print("ERR: --set-status needs --instruction-id and --status")
            return 2
        return set_status(a)
    if a.update_outcomes:
        return update_outcomes()
    return list_tail(a)


if __name__ == "__main__":
    sys.exit(main())
