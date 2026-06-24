#!/usr/bin/env python3
"""Build the dashboard "Intel" data files from raw MCP dumps saved to /tmp.

Additive enrichment, separate from mcp_refresh.py so a failure here never breaks
the core portfolio refresh. Each section is independent and resilient: if its
input dump is missing or malformed, the existing data file is left untouched
(so a transient gap never blanks a panel).

Inputs (raw MCP tool outputs, saved verbatim by the routine):
  /tmp/ibkr_snap_<SYM>.json   <- get_price_snapshot   (CPER,SLV,GLD,PALL,LIT,REMX)
  /tmp/tipranks_consensus.json<- TipRanks ask: consensus + price target, ALB & SQM
  /tmp/tipranks_news_<TKR>.json<- TipRanks ask: recent news sentiment, per ticker
  /tmp/macro_fed.json          <- macro_feedoracle fed_rates_v2
  /tmp/macro_yield.json        <- macro_feedoracle yield_curve_v3
  /tmp/macro_inflation.json    <- macro_feedoracle inflation_v3
  /tmp/macro_stress.json       <- macro_feedoracle market_stress_v1

Outputs: data/{commodities,analysts,macro,news}.json
"""
import json, datetime, pathlib

SRC = pathlib.Path("/tmp")
DATA = pathlib.Path(__file__).resolve().parent.parent / "data"

# display name -> commodity ETF proxy ticker (IBKR snapshot dump)
COMMODITIES = [
    ("Copper", "CPER"), ("Silver", "SLV"), ("Gold", "GLD"),
    ("Palladium", "PALL"), ("Lithium", "LIT"), ("Rare Earth", "REMX"),
]
NEWS_TICKERS = ["ALB", "SQM"]
NEWS_MAX = 12


def _read(name):
    return json.loads((SRC / name).read_text())


def _write(name, payload, now):
    (DATA / name).write_text(json.dumps({"updatedAt": now, **payload}, indent=2))


def _keep(name):
    """Return True if data/<name> already exists (so we preserve it on failure)."""
    return (DATA / name).exists()


def build_commodities(now):
    items = []
    for label, sym in COMMODITIES:
        try:
            d = _read(f"ibkr_snap_{sym}.json")
            price = d.get("last", {}).get("price")
            chg = d.get("change", {}) or {}
            if price is None:
                continue
            items.append({
                "name": label, "symbol": sym,
                "price": round(float(price), 2),
                "change": round(float(chg.get("change", 0) or 0), 2),
                "changePct": round(float(chg.get("change_pct", 0) or 0), 2),
            })
        except Exception:
            continue
    if items:
        _write("commodities.json", {"items": items}, now)
        return len(items)
    return 0


def _consensus_rows(raw):
    """Flatten TipRanks consensus output into one row per ticker (deduped)."""
    rows, seen = [], set()
    for q in raw if isinstance(raw, list) else []:
        for d in (q.get("data") or []):
            tkr = d.get("ticker")
            if not tkr or tkr in seen:
                continue
            seen.add(tkr)
            rows.append({
                "ticker": tkr,
                "name": d.get("companyName", tkr),
                "consensus": d.get("consensus", "—"),
                "priceTarget": d.get("priceTarget"),
                "upside": d.get("priceTargetUpside"),
                "low": d.get("lowPriceTarget"),
                "high": d.get("highPriceTarget"),
                "buy": d.get("buy", 0), "hold": d.get("hold", 0), "sell": d.get("sell", 0),
                "analysts": d.get("totalAnalysts"),
            })
    return rows


def build_analysts(now):
    try:
        rows = _consensus_rows(_read("tipranks_consensus.json"))
    except Exception:
        return 0
    if rows:
        _write("analysts.json", {"items": rows}, now)
        return len(rows)
    return 0


def build_news(now):
    items = []
    for tkr in NEWS_TICKERS:
        try:
            raw = _read(f"tipranks_news_{tkr}.json")
        except Exception:
            continue
        for q in raw if isinstance(raw, list) else []:
            for d in (q.get("data") or []):
                title = d.get("title")
                if not title:
                    continue
                items.append({
                    "ticker": tkr,
                    "title": title,
                    "sentiment": d.get("recommendation", "Neutral"),
                    "date": d.get("recommendationDate", ""),
                    "firm": d.get("firmName", ""),
                    "url": d.get("url", ""),
                })
    # newest first, cap the feed
    items.sort(key=lambda x: x["date"], reverse=True)
    items = items[:NEWS_MAX]
    if items:
        _write("news.json", {"items": items}, now)
        return len(items)
    return 0


def _g(d, *path, default=None):
    for k in path:
        d = d.get(k, {}) if isinstance(d, dict) else {}
    return d if d not in ({}, None) else default


def build_macro(now):
    items = []
    # Fed funds
    try:
        d = _read("macro_fed.json").get("data", {})
        rate = d.get("fed_funds_rate")
        sig = _g(d, "interpretation", "signal", default="")
        pred = d.get("rate_prediction", "")
        if rate is not None:
            items.append({"label": "Fed Funds Rate", "value": f"{rate:.2f}%",
                          "sub": " · ".join(x for x in [sig, pred] if x).lower() or "—",
                          "tone": "good" if str(sig).lower() == "dovish" else "warn" if str(sig).lower() == "hawkish" else "neutral"})
    except Exception:
        pass
    # CPI
    try:
        d = _read("macro_inflation.json").get("data", {})
        v = _g(d, "decision_signal", "current_value")
        band = _g(d, "decision_signal", "risk", "band", default="")
        if v is not None:
            items.append({"label": "CPI (YoY)", "value": f"{v:.2f}%",
                          "sub": ("above 2% target" if v > 2 else "at/below target"),
                          "tone": "warn" if v > 3 else "neutral"})
    except Exception:
        pass
    # Yield curve 10Y-2Y
    try:
        d = _read("macro_yield.json").get("data", {})
        v = _g(d, "decision_signal", "current_value")
        inv = _g(d, "decision_signal", "inversion_context", "inversion_in_last_90d", default=False)
        if v is not None:
            items.append({"label": "10Y–2Y Spread", "value": f"{v:+.2f}",
                          "sub": ("inverted" if (inv or v < 0) else "normal curve"),
                          "tone": "warn" if (inv or v < 0) else "good"})
    except Exception:
        pass
    # Market stress (VIX)
    try:
        d = _read("macro_stress.json").get("data", {})
        vix = _g(d, "decision_signal", "components", "vix")
        if vix is not None:
            items.append({"label": "VIX", "value": f"{vix:.1f}",
                          "sub": ("calm" if vix < 20 else "elevated" if vix < 30 else "stressed"),
                          "tone": "good" if vix < 20 else "warn" if vix < 30 else "bad"})
    except Exception:
        pass
    if items:
        _write("macro.json", {"items": items}, now)
        return len(items)
    return 0


def main():
    now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
    c = build_commodities(now)
    a = build_analysts(now)
    n = build_news(now)
    m = build_macro(now)
    print(f"Enriched @ {now}: commodities={c} analysts={a} news={n} macro={m} "
          f"(0 = kept existing)")


if __name__ == "__main__":
    main()
