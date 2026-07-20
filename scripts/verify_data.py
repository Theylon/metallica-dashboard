#!/usr/bin/env python3
"""Cross-file consistency gate for data/*.json — run before every deploy.

Asserts the identities that make the dashboard's numbers trustworthy:
account KPIs reconcile to the positions table, pnl.json carries the schema
risk.py needs, the benchmark set is the canonical four, and micro.json's
held book matches the live book. Hard failures exit 1 (the Action runs this
before committing/deploying, so broken data never ships); soft issues print
as WARN and don't block.

Stdlib only. Run: python3 scripts/verify_data.py
"""
import datetime
import json
import pathlib
import sys

DATA = pathlib.Path(__file__).resolve().parent.parent / "data"
BENCH_TICKERS = {"SPY", "XME", "SLV", "CPER"}
CENTS = 0.02            # tolerance for sums of independently-rounded cents
# nav comes from a different IBKR endpoint than the position marks, snapshotted
# moments apart — when marks are moving (pre-market, volatile opens) the two
# legitimately disagree by a few basis points. 2026-07-20 pre-market: $17.73
# skew (0.16% of NAV) failed two deploys in a row at the old ±max($10, 0.10%)
# band while every identity check passed. ±0.25% still fails hard on real
# breakage (a dropped position is whole percents), without blocking deploys on
# inherent endpoint skew.
NAV_RESIDUAL_MAX = 10.0        # $ floor for tiny NAVs
NAV_RESIDUAL_PCT = 0.0025      # fraction of |nav|

FAILS, WARNS = [], []


def _load(name):
    return json.loads((DATA / name).read_text())


def fail(msg):
    FAILS.append(msg)
    print(f"FAIL  {msg}")


def warn(msg):
    WARNS.append(msg)
    print(f"WARN  {msg}")


def ok(msg):
    print(f"ok    {msg}")


def base_ticker(t):
    return t.split(" @")[0]


def check_account(account, positions):
    pos_unreal = round(sum(p["unrealizedPnl"] for p in positions), 2)
    if abs(account["unrealizedPnl"] - pos_unreal) <= CENTS:
        ok(f"account.unrealizedPnl {account['unrealizedPnl']} == Σ positions {pos_unreal}")
    else:
        fail(f"account.unrealizedPnl {account['unrealizedPnl']} != Σ positions {pos_unreal}")

    closed = account.get("dailyPnlClosed")
    if closed is None:
        warn("account.dailyPnlClosed missing (pre-fix schema) — treating as 0")
        closed = 0.0
    pos_daily = round(sum(p["dailyPnl"] for p in positions), 2)
    total = round(pos_daily + closed, 2)
    if abs(account["dailyPnl"] - total) <= CENTS:
        ok(f"account.dailyPnl {account['dailyPnl']} == Σ table {pos_daily} + closed {closed}")
    else:
        fail(f"account.dailyPnl {account['dailyPnl']} != Σ table {pos_daily} + closed {closed} = {total}")

    nav, cash = account["nav"], account["cash"]
    residual = round(nav - (cash + sum(p["mktValue"] for p in positions)), 2)
    limit = max(NAV_RESIDUAL_MAX, abs(nav) * NAV_RESIDUAL_PCT)
    if abs(residual) <= limit:
        ok(f"nav residual {residual} within ±{limit:.2f} (nav {nav} vs cash+Σmv)")
    else:
        fail(f"nav residual {residual} exceeds ±{limit:.2f} (nav {nav}, cash {cash})")
    stored = account.get("navResidual")
    if stored is not None and abs(stored - residual) > CENTS:
        warn(f"stored navResidual {stored} != recomputed {residual}")

    navd = nav or 1
    gross = round(sum(abs(p["mktValue"]) for p in positions) / navd * 100, 2)
    if abs(account["grossExposurePct"] - gross) <= 0.1:
        ok(f"grossExposurePct {account['grossExposurePct']} == Σ|mv|/nav {gross}")
    else:
        fail(f"grossExposurePct {account['grossExposurePct']} != Σ|mv|/nav {gross}")


def check_pnl(pnl, account):
    if not isinstance(pnl, list) or not pnl:
        fail("pnl.json is empty or not a list")
        return
    stamps = [p["timestamp"] for p in pnl]
    if stamps != sorted(stamps):
        fail("pnl.json timestamps are not sorted")
    else:
        ok(f"pnl.json sorted, {len(pnl)} points")
    bad_nav = [p for p in pnl if not isinstance(p.get("nav"), (int, float))]
    if bad_nav:
        fail(f"pnl.json has {len(bad_nav)} rows without numeric nav")
    no_twr = [p for p in pnl if not isinstance(p.get("twr"), (int, float))]
    if len(no_twr) > 1:  # intraday carry rows may legitimately lack twr
        warn(f"pnl.json has {len(no_twr)} rows without numeric twr (risk.py skips them)")
    twr_days = {}
    for p in pnl:
        if isinstance(p.get("twr"), (int, float)):
            twr_days[p["timestamp"][:10]] = p["twr"]
    days = sorted(twr_days)
    flat_lead = 0
    for i in range(1, len(days)):
        if twr_days[days[i]] == twr_days[days[0]]:
            flat_lead += 1
        else:
            break
    if flat_lead > 1:
        fail(f"pnl.json has {flat_lead} leading flat placeholder days (should be ≤1)")
    else:
        ok("pnl.json leading flat prefix ≤ 1 baseline row")
    if abs(pnl[-1]["nav"] - account["nav"]) <= CENTS:
        ok(f"pnl last point nav {pnl[-1]['nav']} == account.nav")
    else:
        fail(f"pnl last point nav {pnl[-1]['nav']} != account.nav {account['nav']}")


def check_benchmarks(bench):
    tickers = set(bench.get("tickers", {}))
    if tickers == BENCH_TICKERS:
        ok(f"benchmarks = {sorted(tickers)}")
    else:
        fail(f"benchmark tickers {sorted(tickers)} != canonical {sorted(BENCH_TICKERS)}")
    upd = bench.get("updatedAt", "")[:10]
    for t, e in bench.get("tickers", {}).items():
        if len(e.get("dates", [])) != len(e.get("closes", [])):
            fail(f"benchmarks {t}: dates/closes length mismatch")
        elif e["dates"] and upd:
            gap = (datetime.date.fromisoformat(upd)
                   - datetime.date.fromisoformat(e["dates"][-1])).days
            if gap > 5:
                warn(f"benchmarks {t}: last close {e['dates'][-1]} is {gap}d behind updatedAt")


def check_micro(micro, positions):
    held_rows = {r["ticker"]: r for r in micro.get("tickers", []) if r.get("held")}
    book = {base_ticker(p["ticker"]): p for p in positions}
    missing = sorted(set(book) - set(held_rows))
    extra = sorted(set(held_rows) - set(book))
    if missing:
        fail(f"micro.json held book missing live positions: {missing}")
    if extra:
        fail(f"micro.json marks tickers held that aren't in the book: {extra}")
    if not missing and not extra:
        ok(f"micro.json held book covers exactly the {len(book)} live positions")
    for t, r in held_rows.items():
        p = book.get(t)
        if not p:
            continue
        pos = r.get("position") or {}
        if pos.get("shares") != p["shares"] or r.get("held") != p["side"]:
            fail(f"micro.json {t}: shares/side {pos.get('shares')}/{r.get('held')} "
                 f"!= book {p['shares']}/{p['side']}")
        mv, live = r.get("heldMv"), p["mktValue"]
        if mv and live and abs(mv / live - 1) > 0.2:
            warn(f"micro.json {t}: heldMv {mv} drifts >20% from book {live} (stale price?)")


def check_categories(positions):
    other = sorted(base_ticker(p["ticker"]) for p in positions if p.get("category") == "Other")
    if other:
        warn(f"held tickers categorized 'Other' (add to CATEGORY in mcp_refresh.py): {other}")
    else:
        ok("no held position falls back to category 'Other'")


def check_process_files():
    """Process-layer files (channel_accuracy/alerts/decision_log/orders) — WARN-only.

    These are additive display layers; a malformed one should never block a
    deploy of the book data, so nothing in here may call fail().
    """
    for name in ("channel_accuracy.json", "alerts.json"):
        p = DATA / name
        if not p.exists():
            continue   # optional until their scripts have run once
        try:
            doc = json.loads(p.read_text())
        except Exception as e:
            warn(f"{name} unparseable: {e}")
            continue
        if not doc.get("updatedAt"):
            warn(f"{name} missing updatedAt")
        if name == "channel_accuracy.json":
            bad = [c.get("id") for c in doc.get("channels", [])
                   if c.get("accuracyPct") is not None
                   and not (0 <= c["accuracyPct"] <= 100)]
            if bad:
                warn(f"channel_accuracy accuracyPct outside [0,100]: {bad}")
            else:
                ok(f"channel_accuracy.json: {len(doc.get('channels', []))} channels sane")
        if name == "alerts.json":
            today = datetime.date.today().isoformat()
            stale = [a.get("ticker") for a in doc.get("items", [])
                     if a.get("type") == "earnings_proximity"
                     and (a.get("earningsDate") or today) < today]
            if stale:
                warn(f"alerts.json has past earnings dates: {stale}")
            else:
                ok(f"alerts.json: {len(doc.get('items', []))} alerts, none stale")

    log = DATA / "decision_log.jsonl"
    if log.exists():
        prev_ts, bad_lines, n = "", 0, 0
        for line in log.read_text().splitlines():
            if not line.strip():
                continue
            n += 1
            try:
                ts = json.loads(line).get("ts") or ""
            except Exception:
                bad_lines += 1
                continue
            if ts < prev_ts:
                warn(f"decision_log.jsonl ts not monotonic near entry {n}")
                prev_ts = ts
            else:
                prev_ts = ts
        if bad_lines:
            warn(f"decision_log.jsonl has {bad_lines} unparseable lines")
        else:
            ok(f"decision_log.jsonl: {n} entries parse, ts monotonic")

    # Orders audit log (rendered by the Orders tab; written by order_log.py).
    # Same shape as the decision-log check: per-line parse + monotonic ts,
    # plus the fixed status vocabulary and the identifying fields.
    log = DATA / "orders.jsonl"
    if log.exists():
        statuses = {"created", "submitted", "filled", "cancelled", "expired"}
        terminal = {"filled", "cancelled", "expired"}
        sources = {"owner", "recommendation", "rebalance", "alert"}
        prev_ts, bad_lines, bad_rows, n = "", 0, 0, 0
        open_ids = {}   # instructionId -> ticker of an order still open (non-terminal)
        dup_open = []
        for line in log.read_text().splitlines():
            if not line.strip():
                continue
            n += 1
            try:
                e = json.loads(line)
            except Exception:
                bad_lines += 1
                continue
            ts = e.get("ts") or ""
            if ts < prev_ts:
                warn(f"orders.jsonl ts not monotonic near entry {n}")
            prev_ts = ts
            trig = e.get("trigger")  # optional (older entries); source vocab fixed
            trig_ok = trig is None or (isinstance(trig, dict)
                                       and trig.get("source") in sources)
            if (e.get("status") not in statuses or not e.get("ticker")
                    or e.get("side") not in ("BUY", "SELL") or not e.get("qty")
                    or not trig_ok):
                bad_rows += 1
            # track instructionIds that are still open — a second open order on the
            # same id can't be targeted by --set-status unambiguously (order_log
            # picks the newest, orphaning the earlier one)
            iid = e.get("instructionId")
            if iid is not None:
                if e.get("status") in terminal:
                    open_ids.pop(str(iid), None)
                else:
                    if str(iid) in open_ids:
                        dup_open.append(f"{iid} ({open_ids[str(iid)]} + {e.get('ticker')})")
                    open_ids[str(iid)] = e.get("ticker")
        if bad_lines:
            warn(f"orders.jsonl has {bad_lines} unparseable lines")
        if bad_rows:
            warn(f"orders.jsonl has {bad_rows} rows with bad status or missing ticker/side/qty")
        if dup_open:
            warn(f"orders.jsonl reuses instructionId across OPEN orders: {', '.join(dup_open)} "
                 f"— --set-status can't target them by id alone (use --ts)")
        if not bad_lines and not bad_rows and not dup_open:
            ok(f"orders.jsonl: {n} instructions parse, statuses valid, ts monotonic, ids unique-while-open")


def check_freshness(account, risk, pnl):
    now = datetime.datetime.now(datetime.timezone.utc)
    try:
        upd = datetime.datetime.fromisoformat(account["updatedAt"])
        age_h = (now - upd).total_seconds() / 3600
        if age_h > 72:
            warn(f"account.json is {age_h:.0f}h old")
        else:
            ok(f"account.json {age_h:.1f}h old")
    except Exception:
        warn("account.updatedAt unparseable")
    if risk is not None:
        twr_days = len({p["timestamp"][:10] for p in pnl
                        if isinstance(p.get("twr"), (int, float))})
        if risk.get("obs", 0) > twr_days:
            fail(f"risk.json obs {risk['obs']} > {twr_days} distinct pnl twr days")
        else:
            ok(f"risk.json obs {risk.get('obs')} ≤ {twr_days} pnl twr days")


def main():
    account = _load("account.json")
    positions = _load("positions.json")["positions"]
    pnl = _load("pnl.json")
    bench = _load("benchmarks.json")
    try:
        micro = _load("micro.json")
    except Exception:
        micro = None
        warn("micro.json missing/unreadable — held-book check skipped")
    try:
        risk = _load("risk.json")
    except Exception:
        risk = None
        warn("risk.json missing/unreadable — obs check skipped")

    check_account(account, positions)
    check_pnl(pnl, account)
    check_benchmarks(bench)
    if micro:
        check_micro(micro, positions)
    check_categories(positions)
    check_process_files()
    check_freshness(account, risk, pnl)

    print(f"\n{len(FAILS)} failure(s), {len(WARNS)} warning(s)")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
