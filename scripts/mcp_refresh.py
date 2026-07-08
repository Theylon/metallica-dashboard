#!/usr/bin/env python3
"""Rebuild data/{positions,account,pnl,benchmarks}.json from raw IBKR MCP outputs.

Used by the SessionStart auto-refresh, the scheduled Routine, and any manual
refresh. In a Claude session: call the IBKR MCP tools, save each raw JSON result
to /tmp, then run this script. It never touches report.json (static content).

Inputs (raw MCP tool outputs, saved verbatim):
  /tmp/ibkr_summary.json        <- get_account_summary
  /tmp/ibkr_positions.json      <- get_account_positions
  /tmp/ibkr_balances.json       <- get_account_balances
  /tmp/ibkr_perf.json           <- get_pa_performance_all_periods
  /tmp/ibkr_bench_<TICKER>.json <- get_price_history (STK, ONE_DAY, THREE_MONTHS)
                                   for SPY, XME, SLV, CPER (optional)
"""
import json, datetime, pathlib

SRC = pathlib.Path("/tmp")
DATA = pathlib.Path(__file__).resolve().parent.parent / "data"

# ticker -> dashboard category badge (mirrors scripts/fetch.py)
CATEGORY = {
    "SQM": "Lithium", "ALB": "Lithium", "SGML": "Lithium", "TSLA": "Lithium",
    "LIT": "Lithium", "BATT": "Lithium",
    "FCX": "Copper", "SCCO": "Copper", "HBM": "Copper", "COPX": "Copper",
    "NUE": "Steel", "CLF": "Steel", "RS": "Steel", "STLD": "Steel",
    "AA": "Aluminum", "CENX": "Aluminum", "KALU": "Aluminum",
    "MP": "Rare Earth", "REMX": "Rare Earth", "UUUU": "Uranium",
    "GLD": "Precious", "SLV": "Precious", "PALL": "Precious", "SBSW": "Precious",
    "BHP": "Diversified", "RIO": "Diversified", "VALE": "Diversified",
    "XME": "Mining ETF",
}

# Benchmark ETFs plotted on the dashboard chart.
BENCH_TICKERS = ["SPY", "XME", "SLV", "CPER"]


def load(name):
    return json.loads((SRC / name).read_text())


def build_benchmarks(now):
    """Rebuild data/benchmarks.json from per-ticker IBKR price-history dumps.

    Reads /tmp/ibkr_bench_<TICKER>.json (raw get_price_history output). A ticker
    whose dump is missing or errored keeps its existing entry, so a transient
    data gap never blanks a line on the chart.
    """
    bench_file = DATA / "benchmarks.json"
    try:
        existing = json.loads(bench_file.read_text()).get("tickers", {})
    except Exception:
        existing = {}

    tickers, refreshed, kept = {}, [], []
    for t in BENCH_TICKERS:
        src = SRC / f"ibkr_bench_{t}.json"
        entry = None
        if src.exists():
            try:
                raw = json.loads(src.read_text())
                times, closes = raw.get("time"), raw.get("close")
                if "error" not in raw and times and closes and len(times) == len(closes):
                    entry = {
                        "dates": [s[:10] for s in times],
                        "closes": [round(float(c), 4) for c in closes],
                    }
            except Exception:
                entry = None
        if entry:
            tickers[t] = entry
            refreshed.append(t)
        elif t in existing:
            tickers[t] = existing[t]
            kept.append(t)

    bench_file.write_text(json.dumps({"updatedAt": now, "tickers": tickers}, indent=2))
    return refreshed, kept


def main():
    now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
    summary = load("ibkr_summary.json")
    posdata = load("ibkr_positions.json")
    balances = load("ibkr_balances.json")
    perf = load("ibkr_perf.json")

    # ── Positions + exposure ──────────────────────────────────────────────
    positions, long_val, short_val = [], 0.0, 0.0
    for p in posdata["positions"]:
        tkr = (p.get("contract_description") or "?").strip()
        qty = float(p.get("position", 0))
        mv = float(p.get("market_value", 0))
        long_val += mv if mv >= 0 else 0
        short_val += abs(mv) if mv < 0 else 0
        positions.append({
            "ticker": tkr, "conid": p.get("contract_id"), "description": tkr,
            "side": "long" if qty >= 0 else "short",
            "shares": abs(qty),
            "avgCost": round(float(p.get("average_price", 0)), 4),
            "lastPrice": round(float(p.get("market_price", 0)), 4),
            "mktValue": round(mv, 2),
            "unrealizedPnl": round(float(p.get("unrealized_pnl", 0)), 2),
            "realizedPnl": round(float(p.get("realized_pnl", 0)), 2),
            "dailyPnl": round(float(p.get("daily_pnl", 0)), 2),
            "currency": p.get("currency", "USD"),
            "category": CATEGORY.get(tkr.upper(), "Other"),
        })
    (DATA / "positions.json").write_text(
        json.dumps({"updatedAt": now, "positions": positions}, indent=2))

    # ── Account ───────────────────────────────────────────────────────────
    nav = float(summary.get("net_liquidation") or 0)
    bal_list = balances.get("balances", []) or [{}]
    bal = next((b for b in bal_list if b.get("currency") in ("BASE", "USD")), bal_list[0])
    daily = round(sum(float(p.get("daily_pnl", 0)) for p in posdata["positions"]), 2)
    navd = nav or 1
    account = {
        "updatedAt": now,
        "nav": round(nav, 2),
        "cash": round(float(summary.get("total_cash_value", 0)), 2),
        "unrealizedPnl": round(float(bal.get("unrealized_pnl", 0)), 2),
        "realizedPnl": round(float(bal.get("realized_pnl", 0)), 2),
        "dailyPnl": daily,
        "longExposure": round(long_val / navd * 100, 2),
        "shortExposure": round(short_val / navd * 100, 2),
        "netExposure": round((long_val - short_val) / navd * 100, 2),
        "grossExposurePct": round((long_val + short_val) / navd * 100, 2),
        "currency": "USD",
    }
    (DATA / "account.json").write_text(json.dumps(account, indent=2))

    # ── P&L history (longest available NAV + TWR series) ──────────────────
    # `twr` is IBKR's cumulative time-weighted return (cps, in %) — the
    # deposit-adjusted performance measure. NAV ratios must never be used for
    # returns: an external cash deposit moves NAV without being a gain.
    periods = perf["accounts"]["account"]["periods"]
    ser = periods.get("1Y") or periods.get("YTD") or periods.get("1M") or periods.get("MTD")
    dates, navs = ser["dates"], ser["nav"]
    cps = ser.get("cps") or [None] * len(dates)
    hist = []
    for i, (d, nv) in enumerate(zip(dates, navs)):
        dt = datetime.datetime(int(d[:4]), int(d[4:6]), int(d[6:8]), 20, 0, 0,
                               tzinfo=datetime.timezone.utc)
        is_last = i == len(dates) - 1
        if is_last:
            # get_pa_performance_all_periods can lag or disagree with the
            # account-summary NAV (they're different IBKR endpoints). Use the
            # same authoritative nav as account.json for "today" so the
            # chart's latest point always matches the KPI cards.
            dt = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
            nv = nav
        hist.append({
            "timestamp": dt.isoformat(), "nav": round(nv, 2),
            "twr": round(cps[i] * 100, 4) if cps[i] is not None else None,
        })

    # Carry forward today's earlier intraday snapshots (accumulated run by run
    # by the hourly routine) so the dashboard's 1D chart shows a real intraday
    # curve. Historical days keep only the official close — yesterday's
    # snapshots fall away automatically once the daily series covers that date.
    today = now[:10]
    try:
        prev = json.loads((DATA / "pnl.json").read_text())
    except Exception:
        prev = []
    carried = [p for p in prev
               if p["timestamp"][:10] == today and p["timestamp"] < hist[-1]["timestamp"]]
    hist = hist[:-1] + carried + hist[-1:]
    (DATA / "pnl.json").write_text(json.dumps(hist, indent=2))

    # ── Benchmarks (refreshed only when /tmp/ibkr_bench_*.json dumps exist) ─
    refreshed, kept = build_benchmarks(now)

    print(f"Refreshed @ {now}: NAV {account['nav']} | dailyPnl {account['dailyPnl']} | "
          f"netExp {account['netExposure']}% | {len(positions)} positions | {len(hist)} pnl pts | "
          f"bench refreshed={','.join(refreshed) or '-'} kept={','.join(kept) or '-'}")


if __name__ == "__main__":
    main()
