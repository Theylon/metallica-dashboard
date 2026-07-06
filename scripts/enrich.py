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
TECH_TICKERS = ["ALB", "SQM"]                       # TrueNorth stock snapshots
METAL_SPOT = [("Lithium", "lithium"), ("Copper", "copper"),
              ("Cobalt", "cobalt"), ("Nickel", "nickel")]   # metalminer spot
RESEARCH_SRC = ["ALB"]                              # Bigdata research dumps
RESEARCH_MAX = 6


def _read(name):
    txt = (SRC / name).read_text()
    try:
        return json.loads(txt)
    except Exception:
        # Tolerate text-wrapped payloads, e.g. TipRanks "Found N result(s):\n\n[...]"
        for ch in "[{":
            i = txt.find(ch)
            if i != -1:
                try:
                    return json.loads(txt[i:])
                except Exception:
                    continue
        raise


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
    """Flatten TipRanks consensus output into one row per ticker (deduped).

    TipRanks ask() responses observed in two shapes: a flat list of
    per-ticker dicts (ticker at top level), or a list of {query, data: [...]}
    wrappers. Handle both, mirroring build_news's candidates fallback.
    """
    rows, seen = [], set()
    for q in raw if isinstance(raw, list) else []:
        candidates = q.get("data") if "data" in q else [q]
        for d in (candidates or []):
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
            # Two observed shapes: a flat list of blog-post dicts (title at
            # top level), or a list of {query, data: [...]} wrappers.
            candidates = q.get("data") if "data" in q else [q]
            for d in (candidates or []):
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


def build_technicals(now):
    """Per-holding price + 50/200-day moving averages from TrueNorth snapshots."""
    items = []
    for tkr in TECH_TICKERS:
        try:
            outer = _read(f"truenorth_{tkr}.json")
            snap = json.loads(outer["result"])["snapshot"] if "result" in outer else outer.get("snapshot", {})
            if snap.get("price") is None:
                continue
            items.append({
                "ticker": tkr,
                "price": round(float(snap["price"]), 2),
                "changePct": round(float(snap.get("change_percentage", 0) or 0), 2),
                "ma50": round(float(snap.get("price_avg_50", 0) or 0), 2),
                "ma200": round(float(snap.get("price_avg_200", 0) or 0), 2),
            })
        except Exception:
            continue
    if items:
        _write("technicals.json", {"items": items}, now)
        return len(items)
    return 0


def build_metals_spot(now):
    """True metal spot prices from metalminer (nested JSON-in-string dumps)."""
    items = []
    for label, key in METAL_SPOT:
        try:
            outer = _read(f"metalminer_{key}.json")
            cp = json.loads(outer["data"]["content"][0]["text"])["data"]["current_prices"][0]
            pr = cp["current_price"]
            items.append({
                "name": label,
                "price": round(float(pr["value"]), 2),
                "currency": (pr.get("currency") or "usd").upper(),
                "unit": pr.get("unit", ""),
                "trend": (cp.get("market_analysis", {}) or {}).get("trend", ""),
                "asOf": (pr.get("as_of_date") or "")[:10],
            })
        except Exception:
            continue
    if items:
        _write("metals_spot.json", {"items": items}, now)
        return len(items)
    return 0


def build_research(now):
    """Broker-research snippets from Bigdata.com search dumps."""
    items = []
    for tkr in RESEARCH_SRC:
        try:
            raw = _read(f"bigdata_{tkr}.json")
        except Exception:
            continue
        for r in (raw.get("results") or []):
            chunks = r.get("chunks") or []
            snippet = " ".join((chunks[0].get("text", "") if chunks else "").split())[:280]
            items.append({
                "ticker": tkr,
                "headline": r.get("headline", ""),
                "source": (r.get("source") or {}).get("name", ""),
                "date": (r.get("timestamp") or "")[:10],
                "snippet": snippet,
                "url": r.get("url", ""),
            })
    items.sort(key=lambda x: x["date"], reverse=True)
    items = items[:RESEARCH_MAX]
    if items:
        _write("research.json", {"items": items}, now)
        return len(items)
    return 0


def main():
    now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
    c = build_commodities(now)
    a = build_analysts(now)
    n = build_news(now)
    m = build_macro(now)
    t = build_technicals(now)
    s = build_metals_spot(now)
    r = build_research(now)
    print(f"Enriched @ {now}: commodities={c} analysts={a} news={n} macro={m} "
          f"technicals={t} spot={s} research={r} (0 = kept existing)")


if __name__ == "__main__":
    main()
