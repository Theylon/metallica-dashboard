#!/usr/bin/env python3
"""Live risk engine — recompute the portfolio's risk metrics from the current book.

Replaces the hand-authored risk block in report.json with an auto-computed data/risk.json,
so vol / beta / VaR / correlation / concentration move with the live positions instead of
being rebuilt by hand. report.json is never touched — its narrative fields (smartMoney,
scenarios, drivers, catalysts, bottomLine) stay hand-authored, and the frontend prefers
risk.json for the metrics while falling back to report.json.

Two tiers, so it degrades gracefully:
  Core (always) — annualized vol, beta vs SPY & XME, 1-day historical VaR, worst day,
    max drawdown, HHI / effective-N. Needs only data/pnl.json (daily TWR), data/benchmarks.json
    and data/positions.json + account.json, all of which already exist.
  Matrix + contributions (only when data/price_history.json is present) — the full NxN
    correlation matrix and each position's share of portfolio risk (component VaR), from the
    held-name close series that micro_refresh.py caches.

Pure Python (stdlib only) so it runs in the GitHub Action; also importable — call
record_and_report() from mcp_refresh.py after positions/account are rewritten.
"""
import datetime
import json
import math
import pathlib

DATA = pathlib.Path(__file__).resolve().parent.parent / "data"
RISK_WINDOW = 90          # trailing trading days for the correlation matrix
Z95, Z99 = 1.645, 2.326
ANNUALIZE = math.sqrt(252)


def _load(name, default):
    p = DATA / name
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text())
    except Exception:
        return default


def _is_otc(ticker):
    return "@PINK" in ticker or "(" in ticker


# ── return series ────────────────────────────────────────────────────────────
def daily_twr_returns(pnl):
    """Collapse pnl.json (mixed daily + intraday) to one TWR return per calendar day.

    Rows without a numeric twr are skipped (rather than KeyError) so a pnl.json
    written in another schema degrades to "no metrics" instead of crashing the
    refresh. Leading flat days (twr unchanged, i.e. pre-inception placeholders)
    are collapsed to a single baseline so they can't inflate the obs count.
    """
    by_day = {}
    for p in pnl:
        if isinstance(p.get("twr"), (int, float)):
            by_day[p["timestamp"][:10]] = p      # chronological → last point of the day wins
    days = sorted(by_day)
    while len(days) > 1 and by_day[days[0]]["twr"] == by_day[days[1]]["twr"]:
        days.pop(0)
    rets, dates = [], []
    for i in range(1, len(days)):
        prev = 1 + by_day[days[i - 1]]["twr"] / 100.0
        cur = 1 + by_day[days[i]]["twr"] / 100.0
        if prev:
            rets.append(cur / prev - 1)
            dates.append(days[i])
    return dates, rets


def close_returns(dates, closes):
    """{date_of_later_close: simple return} from an aligned dates/closes pair."""
    out = {}
    for i in range(1, len(closes)):
        a, b = closes[i - 1], closes[i]
        if a:
            out[dates[i]] = b / a - 1.0
    return out


# ── stats primitives (pure python, ~26 names) ────────────────────────────────
def _mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def _std(xs):
    if len(xs) < 2:
        return 0.0
    m = _mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def beta(port_by_date, bench_by_date):
    common = sorted(set(port_by_date) & set(bench_by_date))
    if len(common) < 3:
        return None
    x = [bench_by_date[d] for d in common]
    y = [port_by_date[d] for d in common]
    mx, my = _mean(x), _mean(y)
    var = sum((xi - mx) ** 2 for xi in x)
    if not var:
        return None
    cov = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    return cov / var


def hist_var(rets, conf):
    """Historical VaR as a (negative) return at the given confidence."""
    if not rets:
        return None
    s = sorted(rets)
    idx = min(max(int((1 - conf) * len(s)), 0), len(s) - 1)
    return s[idx]


def max_drawdown_twr(pnl):
    by_day = {}
    for p in pnl:
        if isinstance(p.get("twr"), (int, float)):
            by_day[p["timestamp"][:10]] = p["twr"]
    if not by_day:
        return None
    curve = [1 + by_day[d] / 100.0 for d in sorted(by_day)]
    peak, mdd = curve[0], 0.0
    for v in curve:
        peak = max(peak, v)
        if peak:
            mdd = min(mdd, v / peak - 1.0)
    return mdd


def hhi_effn(positions, nav):
    gross = sum(abs(p["mktValue"]) for p in positions)
    if not gross:
        return None, None
    ssq = sum((abs(p["mktValue"]) / gross) ** 2 for p in positions)
    return round(ssq * 10000, 0), (1 / ssq if ssq else None)


# ── correlation matrix + risk contributions (needs price_history.json) ───────
def _aligned_returns(price_hist, tickers):
    """Per-ticker return dict keyed by date, trailing RISK_WINDOW, for given tickers."""
    rets = {}
    for t in tickers:
        s = price_hist.get(t)
        if not s or len(s.get("closes", [])) < 3:
            continue
        d, c = s["dates"][-(RISK_WINDOW + 1):], s["closes"][-(RISK_WINDOW + 1):]
        rets[t] = close_returns(d, c)
    return rets


def _cov_corr(rets, tickers):
    """Covariance + correlation over the common dates of all `tickers`."""
    common = None
    for t in tickers:
        ds = set(rets[t])
        common = ds if common is None else (common & ds)
    common = sorted(common or [])
    if len(common) < 3:
        return None, None, common
    cols = {t: [rets[t][d] for d in common] for t in tickers}
    means = {t: _mean(cols[t]) for t in tickers}
    n = len(common)
    cov = {}
    for a in tickers:
        for b in tickers:
            cov[(a, b)] = sum((cols[a][k] - means[a]) * (cols[b][k] - means[b])
                              for k in range(n)) / (n - 1)
    corr = {}
    for a in tickers:
        for b in tickers:
            da, db = math.sqrt(cov[(a, a)]), math.sqrt(cov[(b, b)])
            corr[(a, b)] = cov[(a, b)] / (da * db) if da and db else 0.0
    return cov, corr, common


def matrix_and_contributions(positions, nav, price_hist):
    held = {p["ticker"]: p for p in positions if not _is_otc(p["ticker"])}
    tickers = sorted(t for t in held if t in price_hist)
    if len(tickers) < 2:
        return None, None, None, None
    rets = _aligned_returns(price_hist, tickers)
    tickers = [t for t in tickers if t in rets]
    if len(tickers) < 2:
        return None, None, None, None
    cov, corr, common = _cov_corr(rets, tickers)
    if cov is None:
        return None, None, None, None

    matrix = {"tickers": tickers,
              "rows": [[round(corr[(a, b)], 2) for b in tickers] for a in tickers]}

    off = [corr[(a, b)] for i, a in enumerate(tickers) for b in tickers[i + 1:]]
    avg_corr = round(_mean(off), 2) if off else None
    pairs = sorted(((round(corr[(a, b)], 2), f"{a} – {b}")
                    for i, a in enumerate(tickers) for b in tickers[i + 1:]),
                   key=lambda kv: kv[0])
    top = [{"pair": p, "v": v} for v, p in pairs[-2:][::-1]]      # 2 most correlated
    bottom = [{"pair": pairs[0][1], "v": pairs[0][0]}] if pairs else []
    correlations = top + bottom

    # signed weights as fraction of NAV (mktValue is already signed by side)
    w = {t: held[t]["mktValue"] / nav for t in tickers}
    sw = {a: sum(cov[(a, b)] * w[b] for b in tickers) for a in tickers}  # (Σw)_i
    port_var = sum(w[a] * sw[a] for a in tickers)                        # wᵀΣw (daily)
    var95_dollar = Z95 * math.sqrt(port_var) * nav if port_var > 0 else 0.0

    contributions = []
    for t in tickers:
        comp = w[t] * sw[t]
        share = comp / port_var if port_var else 0.0
        contributions.append({
            "ticker": t,
            "side": held[t]["side"],
            "weightPct": round(w[t] * 100, 1),
            "riskContribPct": round(share * 100, 1),
            "mVaR": round(share * var95_dollar, 1),      # component of the 1-day 95% VaR ($)
        })
    contributions.sort(key=lambda c: -c["riskContribPct"])
    return matrix, avg_corr, correlations, contributions


# ── assemble ─────────────────────────────────────────────────────────────────
def _fmt_usd(x):
    return f"-${abs(x):,.0f}" if x < 0 else f"${x:,.0f}"


def build_risk():
    pnl = _load("pnl.json", [])
    bench = _load("benchmarks.json", {}).get("tickers", {})
    positions = _load("positions.json", {}).get("positions", [])
    account = _load("account.json", {})
    price_hist = _load("price_history.json", {}).get("tickers", {})
    nav = account.get("nav") or (pnl[-1]["nav"] if pnl else 0) or 1.0

    dates, rets = daily_twr_returns(pnl)
    port_by_date = dict(zip(dates, rets))
    ann_vol = _std(rets) * ANNUALIZE if len(rets) >= 2 else None
    var95 = hist_var(rets, 0.95)
    var99 = hist_var(rets, 0.99)
    worst = min(rets) if rets else None
    mdd = max_drawdown_twr(pnl) if pnl else None
    hhi, effn = hhi_effn(positions, nav)

    def bench_ret(tkr):
        e = bench.get(tkr)
        return close_returns(e["dates"], e["closes"]) if e else {}
    beta_spy = beta(port_by_date, bench_ret("SPY"))
    beta_xme = beta(port_by_date, bench_ret("XME"))

    matrix, avg_corr, correlations, contributions = matrix_and_contributions(
        positions, nav, price_hist)
    covered = matrix["tickers"] if matrix else []
    n_otc = sum(1 for p in positions if _is_otc(p["ticker"]))

    metrics = []
    if ann_vol is not None:
        metrics.append({"k": "Annualized volatility", "v": f"{ann_vol * 100:.1f}%",
                        "note": f"from the account's daily TWR, {len(rets)} daily obs since inception",
                        "tone": "neutral"})
    if beta_spy is not None:
        metrics.append({"k": "Beta vs S&P 500 (SPY)", "v": f"{beta_spy:.2f}",
                        "note": f"{len(set(port_by_date) & set(bench_ret('SPY')))} overlapping daily obs",
                        "tone": "neutral"})
    if beta_xme is not None:
        metrics.append({"k": "Beta vs metals (XME)", "v": f"{beta_xme:.2f}",
                        "note": "long/short damps directional metals beta",
                        "tone": "pos" if beta_xme < 0.5 else "neutral"})
    if avg_corr is not None:
        metrics.append({"k": "Avg pairwise correlation", "v": f"{avg_corr:.2f}",
                        "note": f"trailing {RISK_WINDOW}d daily returns, {len(covered)} of "
                                f"{len(positions)} holdings ({n_otc} OTC ex.)",
                        "tone": "pos" if avg_corr < 0.55 else "neutral"})
    if var95 is not None:
        note = f"{var95 * 100:.2f}% of NAV"
        if var99 is not None:
            note += f"; 99% VaR {var99 * 100:.2f}% ({_fmt_usd(var99 * nav)})"
        metrics.append({"k": "1-day VaR (95%, historical)", "v": _fmt_usd(var95 * nav),
                        "note": note, "tone": "neg"})
    if worst is not None:
        metrics.append({"k": "Worst day since inception", "v": f"{worst * 100:.2f}%",
                        "note": "single worst daily TWR", "tone": "neg"})
    if mdd is not None:
        metrics.append({"k": "Max drawdown (inception curve)", "v": f"{mdd * 100:.1f}%",
                        "note": "peak-to-trough on the cumulative TWR", "tone": "neg"})
    if hhi is not None:
        metrics.append({"k": "Concentration (HHI / eff. N)", "v": f"{hhi:.0f} / {effn:.1f}",
                        "note": f"{len(positions)} names, ~{effn:.1f} effective", "tone": "pos"})

    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    risk = {
        "updatedAt": now,
        "asOf": (positions and positions_asof()) or now[:10],
        "window": RISK_WINDOW,
        "obs": len(rets),
        "headline": {
            "annVol": round(ann_vol * 100, 1) if ann_vol is not None else None,
            "betaSpy": round(beta_spy, 2) if beta_spy is not None else None,
            "betaXme": round(beta_xme, 2) if beta_xme is not None else None,
            "var1d95": round(var95 * nav) if var95 is not None else None,
            "var1d99": round(var99 * nav) if var99 is not None else None,
            "hhi": hhi, "effectiveN": round(effn, 1) if effn else None,
        },
        "metrics": metrics,
        "avgCorr": avg_corr,
        "correlations": correlations or [],
        "matrix": matrix,
        "contributions": contributions or [],
        "coverageNote": (f"{len(covered)} of {len(positions)} holdings"
                         + (f" ({n_otc} OTC excluded)" if n_otc else "")) if covered
                        else f"correlation matrix pending price_history.json ({len(positions)} holdings)",
    }
    return risk


def positions_asof():
    return _load("positions.json", {}).get("updatedAt", "")[:10]


def write_risk():
    risk = build_risk()
    (DATA / "risk.json").write_text(json.dumps(risk, indent=1) + "\n")
    return risk


def record_and_report():
    """Entry point for mcp_refresh.py (mirrors exposure.record_and_report)."""
    return write_risk()


if __name__ == "__main__":
    r = write_risk()
    h = r["headline"]
    print(f"risk.json: vol {h['annVol']}% · βSPY {h['betaSpy']} · βXME {h['betaXme']} · "
          f"VaR95 ${h['var1d95']} · HHI {h['hhi']}/{h['effectiveN']} · "
          f"matrix {'yes' if r['matrix'] else 'pending'} ({len(r['contributions'])} contribs)")
