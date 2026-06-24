#!/usr/bin/env python3
"""Rebuild data/{positions,account,pnl}.json from raw IBKR MCP tool outputs.

Used by the SessionStart auto-refresh (and any manual refresh). In a Claude
session: call the IBKR MCP tools and save each raw JSON result to /tmp, then run
this script. It does NOT touch benchmarks.json or report.json.

Inputs (raw MCP tool outputs, saved verbatim):
  /tmp/ibkr_summary.json    <- get_account_summary
  /tmp/ibkr_positions.json  <- get_account_positions
  /tmp/ibkr_balances.json   <- get_account_balances
  /tmp/ibkr_perf.json       <- get_pa_performance_all_periods
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


def load(name):
    return json.loads((SRC / name).read_text())


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

    # ── P&L history (longest available NAV series) ────────────────────────
    periods = perf["accounts"]["account"]["periods"]
    ser = periods.get("1M") or periods.get("MTD") or periods.get("YTD")
    dates, navs = ser["dates"], ser["nav"]
    base = navs[0] or 10000
    hist, prev = [], None
    for i, (d, nv) in enumerate(zip(dates, navs)):
        dt = datetime.datetime(int(d[:4]), int(d[4:6]), int(d[6:8]), 20, 0, 0,
                               tzinfo=datetime.timezone.utc)
        if i == len(dates) - 1:
            dt = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
        hist.append({
            "timestamp": dt.isoformat(), "nav": round(nv, 2),
            "unrealizedPnl": round(nv - base, 2), "realizedPnl": 0.0,
            "dailyPnl": 0.0 if prev is None else round(nv - prev, 2),
            "totalPnl": round(nv - base, 2),
        })
        prev = nv
    (DATA / "pnl.json").write_text(json.dumps(hist, indent=2))

    print(f"Refreshed @ {now}: NAV {account['nav']} | dailyPnl {account['dailyPnl']} | "
          f"netExp {account['netExposure']}% | {len(positions)} positions | {len(hist)} pnl pts")


if __name__ == "__main__":
    main()
