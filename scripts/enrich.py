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


# ══════════════════════════════════════════════════════════════════════════════
# Feature E — automated research layer: per-holding events/sentiment, positioning,
# and a rolling macro-regime series. Holdings are read from positions.json so the
# feeds cover the whole book, not a hardcoded pair. Each builder is independent and
# no-ops on missing dumps, exactly like the feeds above.
# ══════════════════════════════════════════════════════════════════════════════
def _holdings():
    """Held tickers, normalized (drop ' @PINK' suffix), for per-name research dumps."""
    try:
        pos = json.loads((DATA / "positions.json").read_text())["positions"]
    except Exception:
        return []
    out = []
    for p in pos:
        t = p["ticker"].split(" @")[0].strip()
        if t and "(" not in t and t not in out:
            out.append(t)
    return out


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _next_earnings(tkr):
    """Earliest upcoming earnings date from an FMP calendar dump (list of {date,symbol})."""
    today = datetime.date.today().isoformat()
    dates = []
    for fname in (f"fmp_cal_{tkr}.json", f"bigdata_cal_{tkr}.json"):
        try:
            raw = _read(fname)
        except Exception:
            continue
        rows = raw if isinstance(raw, list) else (raw.get("data") or raw.get("events") or [])
        for r in rows if isinstance(rows, list) else []:
            d = r.get("date") or r.get("eventDate") or r.get("startDate")
            if d and str(d)[:10] >= today:
                dates.append(str(d)[:10])
    return min(dates) if dates else None


def _sentiment(tkr):
    """Best-effort overall sentiment (score in [-1,1] + label) from a Bigdata tearsheet."""
    try:
        raw = _read(f"bigdata_sent_{tkr}.json")
    except Exception:
        return None, None
    # probe a few likely locations without assuming one exact shape
    for path in (("overall_sentiment", "score"), ("sentiment", "score"), ("summary", "sentiment"),
                 ("score",), ("average_sentiment",), ("sentiment_score",)):
        v = _g(raw, *path) if len(path) > 1 else (raw.get(path[0]) if isinstance(raw, dict) else None)
        s = _num(v)
        if s is not None:
            label = ("Positive" if s > 0.1 else "Negative" if s < -0.1 else "Neutral")
            return round(s, 2), label
    return None, None


def _recent_news(tkr):
    """Recent headlines from an FMP news dump (list of {title,publishedDate,url,site})."""
    try:
        raw = _read(f"fmp_news_{tkr}.json")
    except Exception:
        return []
    rows = raw if isinstance(raw, list) else (raw.get("data") or raw.get("content") or [])
    items = []
    for r in rows if isinstance(rows, list) else []:
        title = r.get("title")
        if not title:
            continue
        items.append({
            "title": " ".join(str(title).split())[:160],
            "date": str(r.get("publishedDate") or r.get("date") or "")[:10],
            "url": r.get("url", ""),
            "sentiment": r.get("sentiment", ""),
        })
    items.sort(key=lambda x: x["date"], reverse=True)
    return items[:4]


def build_events(now):
    items = []
    for tkr in _holdings():
        score, label = _sentiment(tkr)
        nxt = _next_earnings(tkr)
        news = _recent_news(tkr)
        if score is None and nxt is None and not news:
            continue
        items.append({"ticker": tkr, "nextEarnings": nxt,
                      "sentimentScore": score, "sentimentLabel": label, "recentNews": news})
    if items:
        _write("events.json", {"items": items}, now)
        return len(items)
    return 0


def build_positioning(now):
    institutional, insider, cot = [], [], []
    for tkr in _holdings():
        # insider transactions (FMP insiderTrades: list of {transactionType, securitiesTransacted})
        try:
            raw = _read(f"fmp_insider_{tkr}.json")
            rows = raw if isinstance(raw, list) else (raw.get("data") or [])
            net = 0.0
            for r in rows if isinstance(rows, list) else []:
                qty = _num(r.get("securitiesTransacted")) or 0
                tt = str(r.get("transactionType") or r.get("acquisitionOrDisposition") or "").upper()
                net += qty if ("P" in tt or "A" == tt or "BUY" in tt) else -qty
            if rows:
                insider.append({"ticker": tkr, "netInsiderShares": round(net),
                                "direction": "buying" if net > 0 else "selling" if net < 0 else "flat",
                                "window": "recent"})
        except Exception:
            pass
        # institutional ownership / 13F summary (best-effort)
        try:
            raw = _read(f"fmp_13f_{tkr}.json")
            d = raw[0] if isinstance(raw, list) and raw else (raw if isinstance(raw, dict) else {})
            own = _num(d.get("ownershipPercent") or d.get("institutionalOwnershipPercentage"))
            chg = _num(d.get("ownershipPercentChange") or d.get("changeInOwnershipPercentage"))
            if own is not None or chg is not None:
                institutional.append({"ticker": tkr, "instOwnPct": own, "qoqChange": chg,
                                      "topBuyers": d.get("topBuyers", []), "topSellers": d.get("topSellers", [])})
        except Exception:
            pass
    # COT for the metals complex (FMP commitmentOfTraders: net spec = noncomm long - short)
    for label, key in [("Gold", "gold"), ("Silver", "silver"), ("Copper", "copper"),
                       ("Platinum", "platinum"), ("Aluminum", "aluminum")]:
        try:
            raw = _read(f"fmp_cot_{key}.json")
            d = raw[0] if isinstance(raw, list) and raw else (raw if isinstance(raw, dict) else {})
            lng = _num(d.get("noncommPositionsLong") or d.get("noncommercialLong"))
            sht = _num(d.get("noncommPositionsShort") or d.get("noncommercialShort"))
            if lng is not None and sht is not None:
                cot.append({"commodity": label, "netSpecPosition": round(lng - sht),
                            "wowChange": _num(d.get("changeInNetPosition")), "extreme": None})
        except Exception:
            continue
    if institutional or insider or cot:
        _write("positioning.json", {"institutional": institutional, "insider": insider, "cot": cot}, now)
        return len(institutional) + len(insider) + len(cot)
    return 0


def _fedval():
    try:
        return _num(_read("macro_fed.json").get("data", {}).get("fed_funds_rate"))
    except Exception:
        return None


def build_macro_history(now):
    """Append today's macro reading to a rolling series (once/day) + a regime label."""
    date = now[:10]
    path = DATA / "macro_history.json"
    hist = {}
    if path.exists():
        try:
            hist = json.loads(path.read_text())
        except Exception:
            hist = {}
    series = hist.get("series") or {"yieldCurve": [], "cpi": [], "fedFunds": [], "stress": []}

    def mv(fname, *p):
        try:
            return _num(_g(_read(fname).get("data", {}), *p))
        except Exception:
            return None
    readings = {
        "yieldCurve": mv("macro_yield.json", "decision_signal", "current_value"),
        "cpi": mv("macro_inflation.json", "decision_signal", "current_value"),
        "fedFunds": _fedval(),
        "stress": mv("macro_stress.json", "decision_signal", "components", "vix"),
    }
    for k, v in readings.items():
        if v is None:
            continue
        arr = series.setdefault(k, [])
        if arr and arr[-1].get("date") == date:
            arr[-1]["v"] = round(v, 3)               # refresh today's point
        else:
            arr.append({"date": date, "v": round(v, 3)})
        series[k] = arr[-400:]

    recession = mv("macro_recession.json", "decision_signal", "current_value")
    yc, vix = readings["yieldCurve"], readings["stress"]
    label = "expansion"
    if yc is not None and yc < 0:
        label = "late-cycle · inverted"
    elif yc is not None and yc < 0.5:
        label = "late-cycle"
    if vix is not None and vix >= 30:
        label = "stress"
    regime = {"label": label, "recessionRisk": recession,
              "marketStress": (None if vix is None else
                               "calm" if vix < 20 else "elevated" if vix < 30 else "stressed")}
    if any(series.values()):
        path.write_text(json.dumps({"updatedAt": now, "regime": regime, "series": series}, indent=1))
        return sum(len(v) for v in series.values())
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
    ev = build_events(now)
    po = build_positioning(now)
    mh = build_macro_history(now)
    print(f"Enriched @ {now}: commodities={c} analysts={a} news={n} macro={m} "
          f"technicals={t} spot={s} research={r} events={ev} positioning={po} "
          f"macroHistory={mh} (0 = kept existing)")


if __name__ == "__main__":
    main()
