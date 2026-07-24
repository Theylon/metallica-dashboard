#!/usr/bin/env python3
"""Behavioral trade journal — turn the IBKR trade blotter into behavior diagnostics.

Reads a raw get_account_trades dump (saved by the Journal routine to
/tmp/ibkr_trades.json), FIFO-matches fills into closed round-trips, and writes
data/journal.json with:
  aggregate — win rate, avg win/loss, profit factor, avg holding period (split by
    winners vs losers → disposition effect), turnover, realized total.
  byName / byCommodity / bySide — realized-P&L attribution.
  best / worst — the five best and worst round-trips.
  shadow — the "Shadow Account": P&L left on the table, i.e. what each exited lot would
    be worth had it been held to today's price (from positions.json / price_history.json).

Additive and resilient like enrich.py: a missing or malformed dump leaves the existing
data/journal.json untouched. Pure transform, no network — run standalone against a
/tmp/ibkr_trades.json, or from the Journal routine after mcp_refresh.py.
"""
import datetime
import json
import math
import pathlib
from collections import defaultdict, deque

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DUMP = pathlib.Path("/tmp/ibkr_trades.json")

# Fractional-share trading leaves sub-milli-share FIFO residuals (e.g. a 0.0002-share
# lot) that close as "round-trips" with ~$0 P&L but pad the trade count and can carry a
# whole commission on a dust lot. Drop anything below this size — the smallest genuine
# fractional round-trip in the book is ~0.04 shares, so 0.01 cleanly isolates the dust.
MIN_ROUND_TRIP_QTY = 0.01

# The book was rebuilt from a long-only lithium basket into the current long/short
# metals strategy on this date. Behavioral stats over the retired era don't describe
# the current strategy (they were dominated by the long-only drawdown), so the primary
# journal is the current era; the full history is kept under the `allTime` key.
INCEPTION = "2026-06-22"


# ── dump parsing (defensive against field-name variants) ─────────────────────
def _first(d, *keys, default=None):
    for k in keys:
        if isinstance(d, dict) and d.get(k) is not None:
            return d[k]
    return default


def _parse_time(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        ts = v / 1000.0 if v > 1e12 else float(v)      # epoch ms vs s
        return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc)
    s = str(v).strip()
    if s.isdigit():
        return _parse_time(int(s))
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S.%f%z",
                "%Y-%m-%d %H:%M:%S", "%Y%m%d-%H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            dt = datetime.datetime.strptime(s.replace("Z", "+0000"), fmt)
            return dt if dt.tzinfo else dt.replace(tzinfo=datetime.timezone.utc)
        except ValueError:
            continue
    try:
        return datetime.datetime.fromisoformat(s)
    except Exception:
        return None


def _norm_side(v):
    s = str(v or "").upper()
    if s in ("BUY", "B", "BOT", "BUYTOOPEN", "BUY_TO_OPEN"):
        return "BUY"
    if s in ("SELL", "S", "SLD", "SELLSHORT", "SELL_SHORT", "SS"):
        return "SELL"
    return "BUY" if "B" in s else "SELL"


def load_trades():
    if not DUMP.exists():
        return None
    raw = json.loads(DUMP.read_text())
    if isinstance(raw, dict):
        raw = _first(raw, "trades", "data", "results", default=[]) or []
    trades = []
    for t in raw:
        sym = _first(t, "symbol", "ticker", "conid", "conidex")
        qty = _first(t, "size", "quantity", "qty", "shares")
        price = _first(t, "price", "avgPrice", "tradePrice")
        if sym is None or qty is None or price is None:
            continue
        trades.append({
            "symbol": str(sym),
            "side": _norm_side(_first(t, "side", "buySell", "direction")),
            "qty": abs(float(qty)),
            "price": float(price),
            "commission": abs(float(_first(t, "commission", "comm", "fee", default=0) or 0)),
            "time": _parse_time(_first(t, "tradeTime", "trade_time", "time", "executionTime", "date")),
        })
    trades = [t for t in trades if t["time"] is not None and t["qty"] > 0]
    trades.sort(key=lambda t: t["time"])
    return trades


# ── FIFO round-trip matching ─────────────────────────────────────────────────
def pair_round_trips(trades):
    books = defaultdict(deque)   # symbol -> deque of open lots [signed_qty, price, time, comm_per_share]
    closed = []
    for tr in trades:
        signed = tr["qty"] if tr["side"] == "BUY" else -tr["qty"]
        comm_ps = tr["commission"] / tr["qty"] if tr["qty"] else 0.0
        book = books[tr["symbol"]]
        remaining = signed
        while remaining != 0 and book and book[0][0] * remaining < 0:
            lot = book[0]
            match = min(abs(remaining), abs(lot[0]))
            is_long = lot[0] > 0                       # long lot closed by a sell
            gross = (tr["price"] - lot[1]) * match if is_long else (lot[1] - tr["price"]) * match
            realized = gross - (lot[3] + comm_ps) * match
            hold_days = None
            if tr["time"] and lot[2]:
                hold_days = round((tr["time"] - lot[2]).total_seconds() / 86400.0, 1)
            notional = lot[1] * match
            closed.append({
                "ticker": tr["symbol"],
                "side": "long" if is_long else "short",
                "qty": match,
                "entry": lot[1], "exit": tr["price"],
                "openDate": lot[2].date().isoformat() if lot[2] else None,
                "closeDate": tr["time"].date().isoformat() if tr["time"] else None,
                "realized": round(realized, 2),
                "pctReturn": round(realized / notional * 100, 1) if notional else None,
                "holdDays": hold_days,
            })
            lot[0] -= math.copysign(match, lot[0])
            remaining -= math.copysign(match, remaining)
            if abs(lot[0]) < 1e-9:
                book.popleft()
        if abs(remaining) > 1e-9:
            book.append([remaining, tr["price"], tr["time"], comm_ps])
    return closed, books


# ── aggregation ──────────────────────────────────────────────────────────────
def _category_map():
    cats = {}
    try:
        for p in json.loads((DATA / "positions.json").read_text())["positions"]:
            cats[p["ticker"]] = p.get("category") or "Other"
    except Exception:
        pass
    return cats


def _current_prices():
    prices = {}
    try:
        for p in json.loads((DATA / "positions.json").read_text())["positions"]:
            if p.get("lastPrice"):
                prices[p["ticker"]] = p["lastPrice"]
    except Exception:
        pass
    try:
        ph = json.loads((DATA / "price_history.json").read_text()).get("tickers", {})
        for t, s in ph.items():
            if t not in prices and s.get("closes"):
                prices[t] = s["closes"][-1]
    except Exception:
        pass
    return prices


def aggregate(closed):
    if not closed:
        return None
    wins = [c for c in closed if c["realized"] > 0]
    losses = [c for c in closed if c["realized"] < 0]
    gross_win = sum(c["realized"] for c in wins)
    gross_loss = -sum(c["realized"] for c in losses)
    hold = [c["holdDays"] for c in closed if c["holdDays"] is not None]
    hold_w = [c["holdDays"] for c in wins if c["holdDays"] is not None]
    hold_l = [c["holdDays"] for c in losses if c["holdDays"] is not None]

    def avg(xs):
        return round(sum(xs) / len(xs), 1) if xs else None

    total_notional = sum(abs(c["entry"] * c["qty"]) for c in closed)
    nav = 1.0
    try:
        nav = json.loads((DATA / "account.json").read_text()).get("nav") or 1.0
    except Exception:
        pass
    span_days = None
    dts = [c["closeDate"] for c in closed if c["closeDate"]]
    if dts:
        d0, d1 = min(dts), max(dts)
        span_days = (datetime.date.fromisoformat(d1) - datetime.date.fromisoformat(d0)).days or 1

    return {
        "closedTrades": len(closed),
        "winRate": round(len(wins) / len(closed), 2),
        "avgWin": round(gross_win / len(wins), 2) if wins else None,
        "avgLoss": round(-gross_loss / len(losses), 2) if losses else None,
        "profitFactor": round(gross_win / gross_loss, 2) if gross_loss else None,
        "avgHoldDays": avg(hold),
        "avgHoldWinDays": avg(hold_w),
        "avgHoldLossDays": avg(hold_l),
        "dispositionEffect": (round(avg(hold_l) - avg(hold_w), 1)
                              if hold_w and hold_l else None),
        "turnover": round(total_notional / nav, 2) if nav else None,
        "tradesPerWeek": round(len(closed) / (span_days / 7.0), 1) if span_days else None,
        "totalRealized": round(sum(c["realized"] for c in closed), 2),
    }


def attribute(closed, cats):
    by_name, by_com, by_side = defaultdict(list), defaultdict(float), defaultdict(lambda: [0.0, 0])
    for c in closed:
        by_name[c["ticker"]].append(c)
        by_com[cats.get(c["ticker"], "Other")] += c["realized"]
        s = by_side[c["side"]]
        s[0] += c["realized"]
        s[1] += 1
    name_rows = []
    for tk, cs in by_name.items():
        w = sum(1 for c in cs if c["realized"] > 0)
        name_rows.append({
            "ticker": tk, "commodity": cats.get(tk, "Other"),
            "realized": round(sum(c["realized"] for c in cs), 2),
            "trades": len(cs), "winRate": round(w / len(cs), 2),
        })
    name_rows.sort(key=lambda r: r["realized"])
    total = sum(abs(v) for v in by_com.values()) or 1.0
    com_rows = sorted(({"commodity": k, "realized": round(v, 2), "share": round(abs(v) / total, 3)}
                       for k, v in by_com.items()), key=lambda r: r["realized"])
    side_rows = {k: {"realized": round(v[0], 2), "trades": v[1]} for k, v in by_side.items()}
    return name_rows, com_rows, side_rows


def shadow_counterfactual(closed, prices):
    items, delta_sum = [], 0.0
    per_ticker = defaultdict(float)
    for c in closed:
        px = prices.get(c["ticker"])
        if px is None:
            continue
        # holding the exited lot to today: long gains (today-exit)*qty, short gains (exit-today)*qty
        d = (px - c["exit"]) * c["qty"] if c["side"] == "long" else (c["exit"] - px) * c["qty"]
        per_ticker[c["ticker"]] += d
        delta_sum += d
    for tk, d in sorted(per_ticker.items(), key=lambda kv: -abs(kv[1])):
        items.append({"ticker": tk, "currentPrice": round(prices[tk], 2), "shadowDelta": round(d, 2)})
    realized_actual = round(sum(c["realized"] for c in closed), 2)
    return {
        "realizedActual": realized_actual,
        "ifHeldToNow": round(realized_actual + delta_sum, 2),
        "edge": round(-delta_sum, 2),          # >0 → exiting beat holding
        "items": items,
    }


# ── build ─────────────────────────────────────────────────────────────────────
def build():
    trades = load_trades()
    if not trades:
        return None
    closed_all = [c for c in pair_round_trips(trades)[0] if c["qty"] >= MIN_ROUND_TRIP_QTY]
    if not closed_all:
        return None
    # Primary journal = the current long/short era, keyed on when the position was
    # OPENED (a trade opened in the retired long-only book but closed after the
    # pivot still belongs to the old era). Excluded trades are preserved under
    # `allTime`. (On the current dump every trade opened post-inception, so nothing
    # is excluded — the filter is a forward-looking guard, honestly noted below.)
    closed = [c for c in closed_all if (c["openDate"] or "9999-99-99") >= INCEPTION]
    if not closed:                     # nothing opened in the current era yet
        closed = closed_all
    cats = _category_map()
    prices = _current_prices()
    by_name, by_com, by_side = attribute(closed, cats)
    ranked = sorted(closed, key=lambda c: c["realized"])
    retired = len(closed_all) - len(closed)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    return {
        "updatedAt": now,
        "era": {"since": INCEPTION, "label": "current long/short book"},
        "aggregate": aggregate(closed),
        "byName": by_name,
        "byCommodity": by_com,
        "bySide": by_side,
        "best": [dict(c) for c in ranked[-5:][::-1]],
        "worst": [dict(c) for c in ranked[:5]],
        "shadow": shadow_counterfactual(closed, prices),
        # full history (both eras) for reference — not shown in the headline stats
        "allTime": {"since": min((c["openDate"] for c in closed_all if c["openDate"]), default=None),
                    "aggregate": aggregate(closed_all)},
        "note": f"{len(closed)} closed round-trips in the current long/short era "
                f"(since {INCEPTION}); {retired} earlier long-only-era trades excluded from "
                f"these stats (see allTime). FIFO-matched from {len(trades)} fills. "
                f"Shadow Account marks exited lots to current price. Analysis only.",
    }


def write():
    j = build()
    if j is None:
        print("journal: no trades dump (/tmp/ibkr_trades.json) — leaving data/journal.json untouched")
        return None
    (DATA / "journal.json").write_text(json.dumps(j, indent=1) + "\n")
    a = j["aggregate"]
    print(f"journal.json: {a['closedTrades']} round-trips · win {a['winRate']*100:.0f}% · "
          f"PF {a['profitFactor']} · disposition {a['dispositionEffect']}d · "
          f"realized ${a['totalRealized']}")
    return j


if __name__ == "__main__":
    write()
