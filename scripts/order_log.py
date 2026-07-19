#!/usr/bin/env python3
"""Order audit log — append-only record of every IBKR order instruction.

Companion to trade_gate.py: after the gate clears and the owner confirms, the
session creates the IBKR order instruction and records it here; when the owner
submits/cancels it in IBKR (or it fills), the status is updated in place. The
result is a complete audit trail of what was ordered, why, what the gate said,
and what became of it — data/orders.jsonl, append-only, one JSON object per
line. Not consumed by the dashboard (no validate_data.py contract); it is the
process record, like decision_log.jsonl.

Usage:
  append (after create_order_instruction):
    python3 scripts/order_log.py --append --ticker SGML --side BUY --qty 10 \
        --order-type LIMIT --limit 10.25 --tif DAY --conid 511477158 \
        --instruction-id 1234 --url https://... \
        --gates "size_order:WARN" --note "owner confirmed in session"
  update (after submission/cancel/fill):
    python3 scripts/order_log.py --set-status --instruction-id 1234 --status submitted
  show recent:
    python3 scripts/order_log.py --list [-n 10]

Statuses: created → submitted → filled | cancelled | expired.
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
STATUSES = ["created", "submitted", "filled", "cancelled", "expired"]


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
        "gates": a.gates or None,      # e.g. "size_order:WARN,earnings_window:FAIL-overridden"
        "note": a.note or None,        # owner rationale / context
    }
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
    # newest matching instruction id wins (ids can recycle across days in theory)
    for e in reversed([x for x in lines if isinstance(x, dict)]):
        if str(e.get("instructionId")) == str(a.instruction_id):
            hit = e
            break
    if hit is None:
        print(f"orders.jsonl: no entry with instructionId {a.instruction_id}")
        return 1
    hit["status"] = a.status
    hit["statusUpdatedAt"] = _now()
    if a.note:
        hit["note"] = (str(hit.get("note")) + " | " if hit.get("note") else "") + a.note
    tmp = LOG.with_suffix(".jsonl.tmp")
    tmp.write_text("\n".join(
        json.dumps(x) if isinstance(x, dict) else x for x in lines) + "\n")
    os.replace(tmp, LOG)
    print(f"orders.jsonl: instruction {a.instruction_id} → {a.status}")
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
        print(f"{e.get('ts', '?')}  {e.get('status', '?'):9}  "
              f"{e.get('side', '?')} {e.get('qty', '?')} {e.get('ticker', '?')} "
              f"@ {e.get('limit') if e.get('limit') is not None else 'MKT'} "
              f"({e.get('tif', '?')})  instr={e.get('instructionId') or '—'}"
              + (f"  note={e['note']}" if e.get("note") else ""))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Append-only order audit log.")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--append", action="store_true")
    mode.add_argument("--set-status", action="store_true")
    mode.add_argument("--list", action="store_true")
    ap.add_argument("--ticker")
    ap.add_argument("--side", choices=["BUY", "SELL"])
    ap.add_argument("--qty", type=float)
    ap.add_argument("--order-type", choices=["LIMIT", "MARKET"])
    ap.add_argument("--limit", type=float, default=None)
    ap.add_argument("--tif", default="DAY")
    ap.add_argument("--conid", type=int, default=None)
    ap.add_argument("--instruction-id", default=None)
    ap.add_argument("--url", default=None)
    ap.add_argument("--status", choices=STATUSES, default=None)
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
    return list_tail(a)


if __name__ == "__main__":
    sys.exit(main())
