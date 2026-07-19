#!/usr/bin/env python3
"""Signal-efficacy scorecard — does each micro sub-score actually predict returns?

Two products, written to data/signal_scorecard.json:

  IC/IR scorecard — reads the daily snapshots in data/micro_history.jsonl and, for
    every sub-score (momentum, commodity, deep, analyst, fundamentals, sentiment, smart,
    quality) and the composite, computes the rank-IC
    (Spearman correlation of the score at date t with the fwdWindow-forward return) and
    the IR (mean IC / std IC). This is the "Alpha Zoo" idea applied to our own signals:
    it tells us which of the eight actually works. It needs history to accrue, so until
    ~minDaysNeeded snapshots exist it reports status="accumulating" and an empty signals
    list — micro_snapshot.py (called from micro_refresh.py) fills the history over time.

  Factor tilt — computable from day one (no history): the book's net exposure to
    momentum / value / quality / size / low-vol, z-scored across the picks universe and
    weighted by signed portfolio weight.

Pure Python (stdlib only) → runs in the GitHub Action. No-ops cheaply when history is thin.
"""
import datetime
import json
import math
import pathlib

DATA = pathlib.Path(__file__).resolve().parent.parent / "data"
FWD_WINDOW = 20          # forward trading days (≈ snapshots) for the IC horizon
MIN_DAYS = 25            # snapshots needed before the scorecard is "ready"
MIN_NAMES = 5            # min cross-section per date to compute a rank-IC
SUBS = ["momentum", "commodity", "deep", "analyst", "fundamentals", "sentiment", "smart", "quality"]


def _load(name, default):
    p = DATA / name
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text())
    except Exception:
        return default


# ── stats ─────────────────────────────────────────────────────────────────────
def _mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def _std(xs):
    if len(xs) < 2:
        return 0.0
    m = _mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def _ranks(xs):
    """Average ranks (1-based), ties share the mean rank."""
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def _pearson(x, y):
    n = len(x)
    if n < 3:
        return None
    mx, my = _mean(x), _mean(y)
    sx = math.sqrt(sum((a - mx) ** 2 for a in x))
    sy = math.sqrt(sum((b - my) ** 2 for b in y))
    if not sx or not sy:
        return None
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy)


def _spearman(x, y):
    return _pearson(_ranks(x), _ranks(y))


# ── IC/IR scorecard ───────────────────────────────────────────────────────────
def load_history():
    path = DATA / "micro_history.jsonl"
    if not path.exists():
        return {}
    by_date = {}
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        by_date.setdefault(r["date"], {})[r["ticker"]] = r
    return by_date


def signal_value(rec, signal):
    if signal == "composite":
        return rec.get("composite")
    return (rec.get("subs") or {}).get(signal)


def scorecard(by_date):
    dates = sorted(by_date)
    signals = SUBS + ["composite"]
    per_signal = {s: {"ics": [], "n": 0} for s in signals}

    for i, d in enumerate(dates):
        fi = i + FWD_WINDOW
        if fi >= len(dates):
            break
        cur, fut = by_date[d], by_date[dates[fi]]
        common = [t for t in cur if t in fut]
        fwd = {}
        for t in common:
            a, b = cur[t].get("priceAnchor"), fut[t].get("priceAnchor")
            if a and b:
                fwd[t] = b / a - 1.0
        if len(fwd) < MIN_NAMES:
            continue
        for s in signals:
            xs, ys = [], []
            for t, fr in fwd.items():
                v = signal_value(cur[t], s)
                if v is not None:
                    xs.append(v)
                    ys.append(fr)
            if len(xs) >= MIN_NAMES:
                ic = _spearman(xs, ys)
                if ic is not None:
                    per_signal[s]["ics"].append(ic)
                    per_signal[s]["n"] += len(xs)

    out = []
    for s in signals:
        ics = per_signal[s]["ics"]
        if not ics:
            continue
        mean_ic, std_ic = _mean(ics), _std(ics)
        ir = mean_ic / std_ic if std_ic else None
        out.append({
            "signal": s,
            "rankIC": round(mean_ic, 3),
            "ic_tstat": round(ir * math.sqrt(len(ics)), 2) if ir is not None else None,
            "IR": round(ir, 2) if ir is not None else None,
            "hitRate": round(sum(1 for ic in ics if ic > 0) / len(ics), 2),
            "n": per_signal[s]["n"],
            "windows": len(ics),
        })
    out.sort(key=lambda r: (r["rankIC"] is None, -(r["rankIC"] or 0)))
    return out


# ── factor tilt (day-1, no history) ───────────────────────────────────────────
def _zmap(raw):
    """{ticker: raw} → {ticker: z-score} across the available names."""
    vals = list(raw.values())
    m, s = _mean(vals), _std(vals)
    if not s:
        return {t: 0.0 for t in raw}
    return {t: (v - m) / s for t, v in raw.items()}


def _is_otc(t):
    return "@PINK" in t or "(" in t


def factor_tilt():
    micro = _load("micro.json", {}).get("tickers", [])
    funds = _load("micro_src/fundamentals.json", {}).get("fundamentals", {})
    price_hist = _load("price_history.json", {}).get("tickers", {})
    positions = _load("positions.json", {}).get("positions", [])
    account = _load("account.json", {})
    nav = account.get("nav") or 1.0

    by_ticker = {r["ticker"]: r for r in micro}

    # raw factor values across the universe
    raw = {"momentum": {}, "value": {}, "quality": {}, "size": {}, "lowVol": {}}
    for r in micro:
        t = r["ticker"]
        subs = r.get("subs") or {}
        if subs.get("momentum") is not None:
            raw["momentum"][t] = subs["momentum"]
        mc = r.get("marketCap")
        if mc and mc > 0:
            raw["size"][t] = math.log(mc)
        f = funds.get(t)
        price = r.get("price")
        if f:
            eps = f.get("earnings_per_share")
            if eps is not None and price:
                raw["value"][t] = eps / price          # earnings yield (higher = cheaper)
            elif f.get("free_cash_flow_margin") is not None:
                raw["value"][t] = f["free_cash_flow_margin"]
            if f.get("return_on_invested_capital") is not None:
                raw["quality"][t] = f["return_on_invested_capital"]
    for t, s in price_hist.items():
        closes = s.get("closes", [])
        rets = [closes[k] / closes[k - 1] - 1 for k in range(1, len(closes)) if closes[k - 1]]
        if len(rets) >= 5:
            raw["lowVol"][t] = -_std(rets) * math.sqrt(252)   # higher = lower vol

    z = {f: _zmap(raw[f]) for f in raw}

    held = [p for p in positions if not _is_otc(p["ticker"])]
    factors = []
    for f in ["momentum", "value", "quality", "size", "lowVol"]:
        zf = z[f]
        port = sum((p["mktValue"] / nav) * zf[p["ticker"]] for p in held if p["ticker"] in zf)
        longs = [zf[p["ticker"]] for p in held if p["side"] == "long" and p["ticker"] in zf]
        shorts = [zf[p["ticker"]] for p in held if p["side"] == "short" and p["ticker"] in zf]
        factors.append({
            "factor": f,
            "portZ": round(port, 2) if zf else None,
            "longZ": round(_mean(longs), 2) if longs else None,
            "shortZ": round(_mean(shorts), 2) if shorts else None,
            "coverage": sum(1 for p in held if p["ticker"] in zf),
        })
    return {"asOf": _load("positions.json", {}).get("updatedAt", "")[:10], "factors": factors}


# ── assemble ──────────────────────────────────────────────────────────────────
def build():
    by_date = load_history()
    days = len(by_date)
    cards = scorecard(by_date) if days > FWD_WINDOW else []
    ready = days >= MIN_DAYS and bool(cards)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    return {
        "updatedAt": now,
        "status": "ready" if ready else "accumulating",
        "daysCollected": days,
        "minDaysNeeded": MIN_DAYS,
        "fwdWindow": FWD_WINDOW,
        "signals": cards if ready else [],
        "factorTilt": factor_tilt(),
    }


def write():
    sc = build()
    (DATA / "signal_scorecard.json").write_text(json.dumps(sc, indent=1) + "\n")
    return sc


if __name__ == "__main__":
    sc = write()
    print(f"signal_scorecard.json: status={sc['status']} days={sc['daysCollected']}/"
          f"{sc['minDaysNeeded']} signals={len(sc['signals'])} "
          f"factors={len(sc['factorTilt']['factors'])}")
