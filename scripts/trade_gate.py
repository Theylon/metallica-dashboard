#!/usr/bin/env python3
"""Pre-trade risk gate — deterministic checks before any IBKR order instruction.

The execution arm of PROCESS.md: a Claude session about to create an IBKR order
instruction (via the IBKR MCP's create_order_instruction) runs the proposed
ticket through this gate first. It encodes the machine-checkable slice of the
hard risk rules (PROCESS.md §4) plus sizing/exposure/fat-finger sanity, so the
judgment call is only ever "do we override a named gate", never "did we forget
to check".

Reads (never writes): data/account.json, data/positions.json,
data/universe.json, data/events.json, data/micro.json. Stdlib only, no network
— live prices are passed in by the caller (--last from get_price_snapshot).

Usage:
    python3 scripts/trade_gate.py --ticker SGML --side BUY --qty 10 \
        --order-type LIMIT --limit 10.25 --last 10.46 [--tif DAY] [--json] \
        [--override size_name_cap,earnings_window]

Exit 0 = no FAIL gates (WARNs allowed — surface them to the owner).
Exit 1 = at least one FAIL gate: do NOT create the instruction unless the owner
         explicitly overrides the named gate (then rerun with --override).
Exit 2 = bad invocation / missing inputs.
"""
from __future__ import annotations

import argparse
import datetime
import json
import pathlib
import sys

DATA = pathlib.Path(__file__).resolve().parent.parent / "data"

# Sector/hedge ETFs the strategy trades that are outside the single-name
# universe (universe.json is producers/single names only).
HEDGE_ETFS = {"XME", "LIT", "BATT", "KARS", "COPX", "REMX",
              "GLD", "SLV", "PALL", "CPER", "SPY"}

# Thresholds (fractions of NAV unless noted). Tuned to the current book size —
# revisit if NAV changes an order of magnitude.
SIZE_WARN, SIZE_FAIL = 0.05, 0.10          # single-order notional
NAME_CAP = 0.10                            # post-trade single-name gross
GROSS_WARN, GROSS_FAIL = 1.20, 1.50        # post-trade book gross exposure
LIMIT_DEV_WARN, LIMIT_DEV_FAIL = 0.03, 0.08  # |limit/last - 1| fat-finger band
EARN_FAIL_DAYS, EARN_WARN_DAYS = 5, 10     # rule 4a window (calendar days)
STALE_HOURS = 12                           # account.json snapshot age


def _load(name):
    try:
        return json.loads((DATA / name).read_text())
    except Exception:
        return None


def _now():
    return datetime.datetime.now(datetime.timezone.utc)


def main() -> int:
    ap = argparse.ArgumentParser(description="Pre-trade risk gate.")
    ap.add_argument("--ticker", required=True)
    ap.add_argument("--side", required=True, choices=["BUY", "SELL"])
    ap.add_argument("--qty", required=True, type=float)
    ap.add_argument("--order-type", default="LIMIT", choices=["LIMIT", "MARKET"])
    ap.add_argument("--limit", type=float, default=None)
    ap.add_argument("--last", type=float, default=None,
                    help="live last/mark price from get_price_snapshot")
    ap.add_argument("--tif", default="DAY")
    ap.add_argument("--override", default="",
                    help="comma-separated gate ids the owner explicitly overrode")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    a = ap.parse_args()

    tkr = a.ticker.upper().strip()
    if a.qty <= 0:
        print("ERR: --qty must be positive (direction comes from --side)")
        return 2
    if a.order_type == "LIMIT" and a.limit is None:
        print("ERR: LIMIT order needs --limit")
        return 2

    account = _load("account.json") or {}
    positions = {p["ticker"]: p
                 for p in (_load("positions.json") or {}).get("positions", [])}
    universe = {r.get("ticker") for r in (_load("universe.json") or {}).get("tickers", [])}
    events = {e.get("ticker"): e
              for e in (_load("events.json") or {}).get("items", []) or []}
    micro = {r.get("ticker"): r
             for r in (_load("micro.json") or {}).get("tickers", []) or []}

    nav = float(account.get("nav") or 0)
    if nav <= 0:
        print("ERR: data/account.json missing or nav<=0 — refresh first (mcp_refresh.py)")
        return 2

    px = a.limit if a.limit is not None else a.last
    pos = positions.get(tkr)
    if px is None and pos:
        px = pos.get("lastPrice")
    if px is None:
        print("ERR: no price — pass --limit and/or --last (from get_price_snapshot)")
        return 2

    overrides = {g.strip() for g in a.override.split(",") if g.strip()}
    gates = []   # (id, level, message); level in PASS/NOTE/WARN/FAIL

    def gate(gid, level, msg):
        if level == "FAIL" and gid in overrides:
            level = "WARN"
            msg += "  [FAIL overridden by owner]"
        gates.append({"id": gid, "level": level, "msg": msg})

    # ── position arithmetic ──────────────────────────────────────────────────
    old_signed = 0.0
    old_gross_name = 0.0
    if pos:
        old_signed = pos["shares"] * (1 if pos["side"] == "long" else -1)
        old_gross_name = abs(float(pos.get("mktValue") or 0))
    new_signed = old_signed + a.qty if a.side == "BUY" else old_signed - a.qty
    notional = px * a.qty
    increasing = abs(new_signed) > abs(old_signed) + 1e-9
    flips = old_signed != 0 and new_signed != 0 and (old_signed > 0) != (new_signed > 0)

    new_gross_name = abs(new_signed) * px
    gross_now = (float(account.get("longExposure") or 0)
                 + float(account.get("shortExposure") or 0)) / 100.0 * nav
    gross_new = gross_now - old_gross_name + new_gross_name

    # ── gates ────────────────────────────────────────────────────────────────
    # snapshot freshness
    try:
        age_h = (_now() - datetime.datetime.fromisoformat(
            account["updatedAt"])).total_seconds() / 3600.0
        if age_h > STALE_HOURS:
            gate("stale_snapshot", "WARN",
                 f"account.json is {age_h:.0f}h old — refresh (mcp_refresh.py) before sizing")
        else:
            gate("stale_snapshot", "PASS", f"account snapshot {age_h:.1f}h old")
    except Exception:
        gate("stale_snapshot", "WARN", "account.json has no parseable updatedAt")

    # known name
    if tkr in universe or tkr in positions or tkr in HEDGE_ETFS:
        gate("known_name", "PASS", "ticker in universe / held book / hedge-ETF list")
    else:
        gate("known_name", "WARN",
             "off-universe name — needs an explicit owner rationale (logged)")
    mrow = micro.get(tkr)
    if mrow and mrow.get("tradable") is False:
        gate("tradable", "FAIL", "micro.json marks this listing not tradable via IBKR US")

    # order size vs NAV
    frac = notional / nav
    lvl = "FAIL" if frac > SIZE_FAIL else "WARN" if frac > SIZE_WARN else "PASS"
    gate("size_order", lvl,
         f"order notional ${notional:,.0f} = {frac * 100:.1f}% NAV "
         f"(warn>{SIZE_WARN:.0%}, fail>{SIZE_FAIL:.0%})")

    # post-trade single-name gross
    nfrac = new_gross_name / nav
    gate("size_name_cap", "FAIL" if nfrac > NAME_CAP else "PASS",
         f"post-trade {tkr} gross ${new_gross_name:,.0f} = {nfrac * 100:.1f}% NAV "
         f"(cap {NAME_CAP:.0%})")

    # post-trade book gross exposure
    gfrac = gross_new / nav
    lvl = "FAIL" if gfrac > GROSS_FAIL else "WARN" if gfrac > GROSS_WARN else "PASS"
    gate("gross_exposure", lvl,
         f"post-trade book gross ≈ {gfrac * 100:.0f}% NAV "
         f"(warn>{GROSS_WARN:.0%}, fail>{GROSS_FAIL:.0%})")

    # price sanity
    if a.order_type == "MARKET":
        gate("order_type", "WARN",
             "MARKET order — prefer LIMIT (thin metals names gap; PLG-class spreads)")
    if a.limit is not None and a.last:
        dev = abs(a.limit / a.last - 1)
        lvl = "FAIL" if dev > LIMIT_DEV_FAIL else "WARN" if dev > LIMIT_DEV_WARN else "PASS"
        gate("limit_vs_last", lvl,
             f"limit {a.limit} vs last {a.last}: {dev * 100:.1f}% away "
             f"(warn>{LIMIT_DEV_WARN:.0%}, fail>{LIMIT_DEV_FAIL:.0%})")
    elif a.limit is not None and not a.last:
        gate("limit_vs_last", "WARN",
             "no --last supplied — pull get_price_snapshot to fat-finger-check the limit")

    # flip through zero
    if flips:
        gate("position_flip", "WARN",
             f"order flips {tkr} through zero ({old_signed:+g} → {new_signed:+g}) — "
             "confirm this isn't a mistyped qty; consider close then open")

    # rule 4a — earnings window (single names only; increasing exposure only)
    if tkr not in HEDGE_ETFS:
        nxt = (events.get(tkr) or {}).get("nextEarnings")
        if increasing and nxt:
            try:
                d = (datetime.date.fromisoformat(str(nxt)[:10]) - _now().date()).days
                if 0 <= d <= EARN_FAIL_DAYS:
                    gate("earnings_window", "FAIL",
                         f"earnings {nxt} in {d}d — hard rule 4a: don't add single-name "
                         "risk into a print")
                elif 0 <= d <= EARN_WARN_DAYS:
                    gate("earnings_window", "WARN", f"earnings {nxt} in {d}d (rule 4a)")
                else:
                    gate("earnings_window", "PASS", f"next earnings {nxt}")
            except Exception:
                gate("earnings_window", "NOTE", f"unparseable nextEarnings: {nxt!r}")
        elif increasing:
            gate("earnings_window", "NOTE",
                 "no earnings date on file (events.json) — verify manually")
        else:
            gate("earnings_window", "PASS", "reducing exposure — de-risking is always allowed")

    # affordability (keys are additive in account.json; skip if absent)
    avail = account.get("availableFunds")
    if avail is not None:
        if a.side == "BUY" and notional > float(avail):
            gate("funds", "FAIL",
                 f"BUY notional ${notional:,.0f} > available funds ${float(avail):,.0f}")
        elif a.side == "SELL" and increasing and notional > float(avail):
            gate("funds", "WARN",
                 f"short adds margin ≈ ${notional:,.0f} vs available ${float(avail):,.0f}")
        else:
            gate("funds", "PASS", f"available funds ${float(avail):,.0f}")

    # rule 4e — macro-bias contradiction is flagged, never blocked
    if mrow:
        bias = next((b.get("bias") for b in
                     (_load("micro.json") or {}).get("commodityBias", []) or []
                     if b.get("material") == mrow.get("material")), None)
        trade_dir = "long" if a.side == "BUY" else "short"
        if increasing and bias in ("long", "short") and bias != trade_dir:
            gate("macro_bias", "WARN",
                 f"{trade_dir} trade vs {bias} {mrow.get('material')} bias — "
                 "micro override, must be logged with rationale (rule 4e)")

    # ── report ───────────────────────────────────────────────────────────────
    fails = [g for g in gates if g["level"] == "FAIL"]
    warns = [g for g in gates if g["level"] == "WARN"]
    ticket = {
        "ticker": tkr, "side": a.side, "qty": a.qty,
        "orderType": a.order_type, "limit": a.limit, "tif": a.tif,
        "price": px, "notional": round(notional, 2),
        "pctNav": round(frac * 100, 2), "conid": (pos or {}).get("conid"),
        "position": {"before": old_signed, "after": new_signed},
        "grossExposureAfterPct": round(gfrac * 100, 1),
        "micro": {"composite": (mrow or {}).get("composite"),
                  "held": (mrow or {}).get("held"),
                  "recommendation": (mrow or {}).get("recommendation")} if mrow else None,
    }

    if a.json:
        print(json.dumps({"ticket": ticket, "gates": gates,
                          "fails": len(fails), "warns": len(warns)}, indent=2))
    else:
        p = pos or {}
        print(f"── ticket ─ {a.side} {a.qty:g} {tkr} @ "
              f"{'MKT' if a.order_type == 'MARKET' else a.limit} ({a.tif}) ─"
              f" ${notional:,.0f} = {frac * 100:.1f}% NAV")
        print(f"   position {old_signed:+g} → {new_signed:+g} shares"
              + (f" (held {p.get('side')})" if pos else " (new name)")
              + f" · book gross after ≈ {gfrac * 100:.0f}% NAV")
        for g in gates:
            print(f"   {g['level']:4} {g['id']}: {g['msg']}")
        print(f"── {'BLOCKED — ' + str(len(fails)) + ' FAIL gate(s)' if fails else 'CLEAR'}"
              + (f" · {len(warns)} warning(s) — surface to owner" if warns else ""))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
