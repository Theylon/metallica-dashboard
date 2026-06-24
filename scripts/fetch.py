#!/usr/bin/env python3
"""
Metallica Dashboard — data fetcher.
Pulls IBKR Web API + Yahoo Finance benchmark data, writes to data/.
Run by GitHub Actions every 30 min during market hours (Mon-Fri 9am-4pm ET).

Required env vars:
  IBKR_CONSUMER_KEY   — your IBKR OAuth consumer key
  IBKR_PRIVATE_KEY    — RSA private key PEM (IBKR OAuth 1.0a / RSA-SHA256)
  IBKR_ACCOUNT_ID     — account number, e.g. U1234567

Optional:
  IBKR_BASE_URL       — override API base (default: https://api.ibkr.com/v1/api)
"""

import base64
import datetime
import json
import os
import time
import uuid
from pathlib import Path
from urllib.parse import quote

import requests
import yfinance as yf
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

IBKR_BASE = os.environ.get("IBKR_BASE_URL", "https://api.ibkr.com/v1/api")
CONSUMER_KEY = os.environ.get("IBKR_CONSUMER_KEY", "")
ACCOUNT_ID = os.environ.get("IBKR_ACCOUNT_ID", "")
PRIVATE_KEY_PEM = os.environ.get("IBKR_PRIVATE_KEY", "")

DATA_DIR = Path(__file__).parent.parent / "data"
BENCHMARK_TICKERS = ["SPY", "XME", "SLV", "CPER", "JJU"]
PNL_WINDOW_DAYS = 90

# Metal category tags — maps ticker → display label used in the dashboard.
METAL_CATEGORIES = {
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

# ---------------------------------------------------------------------------
# IBKR OAuth 1.0a with RSA-SHA256
# ---------------------------------------------------------------------------

_private_key = None


def _get_private_key():
    global _private_key
    if _private_key is None:
        _private_key = serialization.load_pem_private_key(
            PRIVATE_KEY_PEM.encode(), password=None
        )
    return _private_key


def _make_oauth_header(method: str, url: str) -> str:
    """Build Authorization header for IBKR OAuth 1.0a / RSA-SHA256."""
    timestamp = str(int(time.time()))
    nonce = uuid.uuid4().hex

    oauth_params = {
        "oauth_consumer_key": CONSUMER_KEY,
        "oauth_nonce": nonce,
        "oauth_signature_method": "RSA-SHA256",
        "oauth_timestamp": timestamp,
    }

    # Signature base string: METHOD & encoded_url & encoded_params
    sorted_params = "&".join(
        f"{quote(k, safe='')}={quote(str(v), safe='')}"
        for k, v in sorted(oauth_params.items())
    )
    base_url = url.split("?")[0]
    sig_base = (
        f"{method.upper()}&"
        f"{quote(base_url, safe='')}&"
        f"{quote(sorted_params, safe='')}"
    )

    sig = _get_private_key().sign(
        sig_base.encode(), padding.PKCS1v15(), hashes.SHA256()
    )
    oauth_params["oauth_signature"] = base64.b64encode(sig).decode()

    parts = ", ".join(
        f'{k}="{quote(str(v), safe="")}"' for k, v in sorted(oauth_params.items())
    )
    return f'OAuth realm="limited_poa", {parts}'


def ibkr_get(path: str) -> dict | list:
    url = f"{IBKR_BASE}{path}"
    resp = requests.get(
        url,
        headers={"Authorization": _make_oauth_header("GET", url)},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


# ---------------------------------------------------------------------------
# Position fetch
# ---------------------------------------------------------------------------


def fetch_positions() -> list[dict]:
    raw = ibkr_get(f"/portfolio/{ACCOUNT_ID}/positions/0")
    positions = []
    for p in raw:
        ticker = p.get("ticker") or p.get("contractDesc", "?")
        mkt_val = float(p.get("mktValue", 0))
        pos_size = float(p.get("position", 0))
        positions.append(
            {
                "ticker": ticker,
                "conid": p.get("conid"),
                "description": p.get("contractDesc", ""),
                "side": "long" if pos_size >= 0 else "short",
                "shares": abs(pos_size),
                "avgCost": round(float(p.get("avgCost", 0)), 4),
                "lastPrice": round(float(p.get("mktPrice", 0)), 4),
                "mktValue": round(mkt_val, 2),
                "unrealizedPnl": round(float(p.get("unrealizedPnl", 0)), 2),
                "realizedPnl": round(float(p.get("realizedPnl", 0)), 2),
                "currency": p.get("currency", "USD"),
                "category": METAL_CATEGORIES.get(ticker.upper(), "Other"),
            }
        )
    return positions


# ---------------------------------------------------------------------------
# Account summary
# ---------------------------------------------------------------------------


def _extract_val(summary: dict, key: str) -> float:
    item = summary.get(key, {})
    if isinstance(item, dict):
        return float(item.get("amount", 0))
    return float(item or 0)


def fetch_account() -> dict:
    summary = ibkr_get(f"/portfolio/{ACCOUNT_ID}/summary")
    return {
        "nav": _extract_val(summary, "netliquidation"),
        "cash": _extract_val(summary, "totalcashvalue"),
        "unrealizedPnl": _extract_val(summary, "unrealizedpnl"),
        "realizedPnl": _extract_val(summary, "realizedpnl"),
        "currency": "USD",
    }


def fetch_daily_pnl() -> float:
    try:
        data = ibkr_get("/iserver/account/pnl/partitioned")
        upnl = data.get("upnl", {})
        acct = upnl.get(ACCOUNT_ID, {})
        return float(acct.get("dpl", 0))
    except Exception as e:
        print(f"  Warning: daily P&L fetch failed: {e}")
        return 0.0


# ---------------------------------------------------------------------------
# Benchmark data (Yahoo Finance, free)
# ---------------------------------------------------------------------------


def fetch_benchmarks() -> dict:
    result = {}

    # Daily closes — 90-day history
    daily = yf.download(
        BENCHMARK_TICKERS, period="90d", auto_adjust=True, progress=False
    )
    closes_daily = daily.get("Close", daily)

    for ticker in BENCHMARK_TICKERS:
        col = (ticker,) if isinstance(closes_daily.columns, type(closes_daily.columns)) else ticker
        series = closes_daily.get(ticker) if ticker in closes_daily else None
        if series is None:
            # Try tuple key (multi-ticker download uses MultiIndex columns)
            try:
                series = closes_daily[ticker]
            except KeyError:
                continue
        series = series.dropna()
        result[ticker] = {
            "dates": [d.strftime("%Y-%m-%d") for d in series.index],
            "closes": [round(float(v), 4) for v in series.values],
        }

    # Intraday closes for today (5-min intervals) — used for 1D chart
    try:
        intraday = yf.download(
            BENCHMARK_TICKERS,
            period="1d",
            interval="5m",
            auto_adjust=True,
            progress=False,
        )
        closes_intra = intraday.get("Close", intraday)
        for ticker in BENCHMARK_TICKERS:
            try:
                s = closes_intra[ticker].dropna()
            except KeyError:
                continue
            if ticker in result:
                result[ticker]["intraday"] = {
                    "timestamps": [t.isoformat() for t in s.index],
                    "closes": [round(float(v), 4) for v in s.values],
                }
    except Exception as e:
        print(f"  Warning: intraday fetch failed: {e}")

    return result


# ---------------------------------------------------------------------------
# P&L history (rolling 90-day append)
# ---------------------------------------------------------------------------


def update_pnl_history(account: dict) -> None:
    pnl_file = DATA_DIR / "pnl.json"
    history = json.loads(pnl_file.read_text()) if pnl_file.exists() else []

    snapshot = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "nav": account["nav"],
        "unrealizedPnl": account["unrealizedPnl"],
        "realizedPnl": account["realizedPnl"],
        "dailyPnl": account["dailyPnl"],
        "totalPnl": account["unrealizedPnl"] + account["realizedPnl"],
    }
    history.append(snapshot)

    cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(
        days=PNL_WINDOW_DAYS
    )
    history = [
        h
        for h in history
        if datetime.datetime.fromisoformat(h["timestamp"]) > cutoff
    ]
    pnl_file.write_text(json.dumps(history, indent=2))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # No credentials → keep the committed data snapshot and let the deploy proceed.
    # Live fetching kicks in automatically once the IBKR_* secrets are set.
    if not (CONSUMER_KEY and ACCOUNT_ID and PRIVATE_KEY_PEM):
        print(f"[{now_str}] No IBKR credentials set — skipping live fetch, "
              "keeping existing data/ snapshot.")
        return

    print(f"[{now_str}] Starting Metallica data fetch")

    # Positions
    print("  Fetching positions...")
    positions = fetch_positions()
    (DATA_DIR / "positions.json").write_text(
        json.dumps({"updatedAt": now_str, "positions": positions}, indent=2)
    )
    print(f"  → {len(positions)} positions")

    # Account
    print("  Fetching account summary...")
    account = fetch_account()
    account["dailyPnl"] = fetch_daily_pnl()

    # Compute exposure from positions
    nav = account["nav"] or 1
    long_val = sum(p["mktValue"] for p in positions if p["mktValue"] > 0)
    short_val = sum(abs(p["mktValue"]) for p in positions if p["mktValue"] < 0)
    account["longExposure"] = round(long_val / nav * 100, 2)
    account["shortExposure"] = round(short_val / nav * 100, 2)
    account["netExposure"] = round((long_val - short_val) / nav * 100, 2)
    account["grossExposurePct"] = round((long_val + short_val) / nav * 100, 2)

    (DATA_DIR / "account.json").write_text(
        json.dumps({"updatedAt": now_str, **account}, indent=2)
    )
    print(f"  → NAV ${account['nav']:,.0f} | daily P&L ${account['dailyPnl']:+,.0f}")

    # P&L history
    print("  Updating P&L history...")
    update_pnl_history(account)

    # Benchmarks
    print("  Fetching benchmark data...")
    benchmarks = fetch_benchmarks()
    (DATA_DIR / "benchmarks.json").write_text(
        json.dumps({"updatedAt": now_str, "tickers": benchmarks}, indent=2)
    )
    print(f"  → {', '.join(benchmarks.keys())}")

    print(f"[{now_str}] Done.")


if __name__ == "__main__":
    main()
