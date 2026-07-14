#!/usr/bin/env python3
"""Build data/micro.json — per-ticker micro-analysis scores for the Stock Picks tab.

Inputs (produced in a Claude session; paths can be overridden with env MICRO_SRC):
  <src>/quotes.json          — FMP batch quotes {ticker: {price, vs50, vs200, range52w, marketCap, suspect...}}
  <src>/commodity_bias.json  — per-material bias layer (long/short/neutral, score -2..+2, evidence)
  <src>/deep_*.json          — per-group deep-dive verdicts (microScore 0-10, thesis, catalysts, risks)
  <src>/discoveries.json     — new tickers not in the Excel universe
  <src>/recommendations.json — hand-curated trade recommendations (optional)
Plus data/universe.json (from scripts/build_universe.py).

Composite micro-score (0-100) = weighted sub-scores (each 0-10):
  momentum 20% · commodity alignment 20% · deep-dive micro 15% · analyst 15%
  · smart score 10% · news sentiment 10% · quality 10%
Missing sub-scores redistribute their weight. Score reads as "attractiveness as a LONG";
a LOW score on a liquid name is a short candidate. Ranked within material group.
"""
import datetime
import glob
import json
import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from micro_score import WEIGHTS, clamp, momentum_score, composite_from_subs, rank_within_groups

DATA = pathlib.Path(__file__).resolve().parent.parent / "data"
# Research inputs live in the repo (data/micro_src) so any session can rebuild
# micro.json deterministically; MICRO_SRC overrides for ad-hoc scratchpad runs.
SRC = pathlib.Path(os.environ.get("MICRO_SRC", str(DATA / "micro_src")))

CONSENSUS_SCORE = {
    "StrongBuy": 10, "Strong Buy": 10, "Buy": 8, "ModerateBuy": 7, "Moderate Buy": 7,
    "Hold": 4, "Neutral": 4, "ModerateSell": 2, "Sell": 0, "StrongSell": 0, "No rating": None,
}
SENTIMENT_SCORE = {
    "VeryBullish": 10, "Bullish": 7.5, "Neutral": 5, "Bearish": 2.5, "VeryBearish": 0,
    "Positive": 7.5, "Negative": 2.5, "Unknown": None,
}
CAP_SCORE = {"Large": 9, "Mid": 7, "Small": 4, "Micro": 2, "large": 9, "mid": 7, "small": 4, "micro": 2}
ROLE_SCORE = {"Producer": 8, "Royalty": 9, "Streaming": 9, "Distributor": 6, "Processor": 6,
              "Consumer": 5, "ETF": 5, "Explorer": 2, "Developer": 3}


def load(name, default):
    p = SRC / name
    if p.exists():
        return json.loads(p.read_text())
    return default


def commodity_score(rec, bias_by_material):
    mats = rec.get("materials") or []
    if not mats:
        return None
    b = bias_by_material.get(mats[0])
    if b is None:
        return None
    linkage = 5.0
    if rec.get("omLinkage") and rec["omLinkage"].get("score") is not None:
        linkage = float(rec["omLinkage"]["score"])
    # bias score -2..+2, scaled by how tightly the stock is coupled to the metal
    return clamp(5.0 + b["score"] * 2.0 * (linkage / 9.0))


def analyst_score(rec, deep):
    # deep-dive analyst refresh wins over the Excel snapshot
    upside, consensus = None, None
    if deep and deep.get("analyst"):
        a = deep["analyst"]
        upside, consensus = a.get("upsidePct"), a.get("consensus")
    tr = rec.get("tipranks") or {}
    if upside is None:
        upside = tr.get("upside")
    if consensus is None:
        consensus = tr.get("consensus")
    parts = []
    if consensus is not None and CONSENSUS_SCORE.get(str(consensus)) is not None:
        parts.append(CONSENSUS_SCORE[str(consensus)])
    if upside is not None:
        try:
            parts.append(clamp(5.0 + float(upside) / 8.0))  # +40% upside saturates
        except (TypeError, ValueError):
            pass
    return round(sum(parts) / len(parts), 1) if parts else None


def smart_score(rec, deep):
    s = None
    if deep and deep.get("analyst") and deep["analyst"].get("smartScore") is not None:
        s = deep["analyst"]["smartScore"]
    elif rec.get("tipranks") and rec["tipranks"].get("smartScore") is not None:
        s = rec["tipranks"]["smartScore"]
    if s is None:
        return None
    try:
        return clamp((float(s) - 1) * 10.0 / 9.0)
    except (TypeError, ValueError):
        return None


def sentiment_score(rec):
    tr = rec.get("tipranks") or {}
    vals = []
    for key in ("newsSentiment", "newsSentimentTR", "newsSentimentMM"):
        v = SENTIMENT_SCORE.get(str(tr.get(key)))
        if v is not None:
            vals.append(v)
    if tr.get("newsScore") is not None:
        try:
            vals.append(clamp(float(tr["newsScore"]) * 10.0))
        except (TypeError, ValueError):
            pass
    return round(sum(vals) / len(vals), 1) if vals else None


def quality_score(rec, q):
    vals = []
    cap = rec.get("capTier")
    if cap and CAP_SCORE.get(str(cap).split()[0]) is not None:
        vals.append(CAP_SCORE[str(cap).split()[0]])
    role = rec.get("role")
    if role and ROLE_SCORE.get(str(role)) is not None:
        vals.append(ROLE_SCORE[str(role)])
    if q and q.get("marketCap"):
        mc = q["marketCap"]
        vals.append(9 if mc > 2e10 else 7 if mc > 2e9 else 5 if mc > 5e8 else 3 if mc > 1.5e8 else 1)
    return round(sum(vals) / len(vals), 1) if vals else None


def fundamentals_score(f):
    """0-10 from TrueNorth annual metrics: profitability + balance sheet + growth."""
    if not f:
        return None
    parts = []
    if f.get("ebitda_margin") is not None:
        parts.append(clamp(f["ebitda_margin"] * 25.0))            # 40% margin = 10
    if f.get("return_on_invested_capital") is not None:
        parts.append(clamp(5.0 + f["return_on_invested_capital"] * 25.0))  # ROIC 20% = 10
    elif f.get("return_on_equity") is not None:
        parts.append(clamp(5.0 + f["return_on_equity"] * 20.0))
    lev = []
    if f.get("net_debt_to_ebitda") is not None:
        lev.append(clamp(8.0 - 1.5 * max(0.0, f["net_debt_to_ebitda"])))   # net cash ~8, 4x+ ~2
    if f.get("debt_to_equity") is not None:
        lev.append(clamp(9.0 - 4.0 * max(0.0, f["debt_to_equity"])))
    if lev:
        parts.append(sum(lev) / len(lev))
    growth = []
    for k in ("revenue_growth_yoy", "ebitda_growth_yoy"):
        if f.get(k) is not None:
            growth.append(clamp(5.0 + f[k] * 10.0))               # +50% growth = 10
    if growth:
        parts.append(sum(growth) / len(growth))
    return round(sum(parts) / len(parts), 1) if parts else None


def tradable(rec, q):
    ex = (rec.get("exchange") or (q.get("exchange") if q else "") or "")
    us = any(k in str(ex).upper() for k in ("NYSE", "NASDAQ", "AMEX", "ADR", "CBOE", "OTC"))
    liquid = bool(q) and not q.get("suspect") and (q.get("marketCap") or 0) > 1.5e8 and (q.get("price") or 0) >= 1
    return us and liquid


# ── AI Hedge Fund layer (concept ported from virattt/ai-hedge-fund, MIT) ─────────────
# hedgeFund = the per-ticker multi-analyst verdict (merged from hedge_*.json).
# hedgeCrossVal = a deterministic cross-check of the primary FMP/TipRanks/TrueNorth
# numbers against an independent Yahoo Finance pull (data/micro_src/yahoo.json).
CONS_DIR = {"StrongBuy": "bull", "Strong Buy": "bull", "Buy": "bull",
            "ModerateBuy": "bull", "Moderate Buy": "bull", "Hold": "neutral",
            "Neutral": "neutral", "ModerateSell": "bear", "Moderate Sell": "bear",
            "Sell": "bear", "StrongSell": "bear", "Strong Sell": "bear"}


def _yahoo_dir(yq):
    k = str(yq.get("recommendationKey") or "").lower()
    if k in ("strong_buy", "buy"):
        return "bull"
    if k in ("sell", "strong_sell", "underperform"):
        return "bear"
    if k in ("hold", "neutral"):
        return "neutral"
    m = yq.get("recommendationMean")
    if isinstance(m, (int, float)):
        return "bull" if m <= 2.5 else "neutral" if m <= 3.5 else "bear"
    return None


def cross_validation(analyst, fundamentals, price, yq):
    """Compare primary (FMP/TipRanks/TrueNorth) numbers to an independent Yahoo pull.

    Returns {agreement, flags[], checks[], yahoo{}} or None when Yahoo has no entry.
    Thresholds: price-target |Δ|>15%, recommendation-direction mismatch, EBITDA-margin
    >5pp, price staleness >10% each raise a flag.
    """
    if not yq:
        return None
    checks, flags = [], []

    pt = (analyst or {}).get("priceTarget")
    ytp = yq.get("targetMean")
    if pt and ytp:
        d = (float(ytp) / float(pt) - 1.0) * 100.0
        status = "agree" if abs(d) <= 15 else "flag"
        checks.append({"field": "priceTarget", "primary": round(float(pt), 2),
                       "yahoo": round(float(ytp), 2), "deltaPct": round(d, 1), "status": status})
        if status == "flag":
            flags.append(f"Price target: Yahoo ${ytp:.0f} vs primary ${pt:.0f} ({d:+.0f}%)")

    pdir = CONS_DIR.get(str((analyst or {}).get("consensus")))
    ydir = _yahoo_dir(yq)
    if pdir and ydir:
        status = "agree" if pdir == ydir else "flag"
        checks.append({"field": "recommendation", "primary": pdir, "yahoo": ydir, "status": status})
        if status == "flag":
            flags.append(f"Rating: Yahoo {ydir} vs primary {pdir}")

    pm = (fundamentals or {}).get("ebitda_margin")
    ym = yq.get("ebitdaMargins")
    if pm is not None and ym is not None:
        dpp = (float(ym) - float(pm)) * 100.0
        status = "agree" if abs(dpp) <= 5 else "flag"
        checks.append({"field": "ebitdaMargin", "primary": round(float(pm), 4),
                       "yahoo": round(float(ym), 4), "deltaPp": round(dpp, 1), "status": status})
        if status == "flag":
            flags.append(f"EBITDA margin: Yahoo {ym * 100:.0f}% vs primary {pm * 100:.0f}% ({dpp:+.0f}pp)")

    yp = yq.get("price")
    if price and yp:
        d = (float(yp) / float(price) - 1.0) * 100.0
        if abs(d) > 10:
            checks.append({"field": "price", "primary": round(float(price), 2),
                           "yahoo": round(float(yp), 2), "deltaPct": round(d, 1), "status": "flag"})
            flags.append(f"Price: Yahoo ${yp:.2f} vs snapshot ${price:.2f} ({d:+.0f}%)")

    rec_mismatch = any(c["field"] == "recommendation" and c["status"] == "flag" for c in checks)
    agreement = "agree" if not flags else ("conflict" if (len(flags) >= 2 or rec_mismatch) else "mixed")
    yahoo_subset = {k: yq.get(k) for k in
                    ("price", "targetMean", "recommendationKey", "recommendationMean",
                     "ebitdaMargins", "returnOnEquity", "numberOfAnalysts") if yq.get(k) is not None}
    return {"agreement": agreement, "flags": flags, "checks": checks, "yahoo": yahoo_subset}


def hedge_block(hf):
    """Normalize a merged hedge entry into the per-ticker hedgeFund block (or None)."""
    if not hf or not hf.get("analysts"):
        return None
    return {"aggregate": hf.get("aggregate"), "analysts": hf.get("analysts"),
            "modelDerived": bool(hf.get("modelDerived")), "asOf": hf.get("asOf")}


def main():
    universe = json.loads((DATA / "universe.json").read_text())
    quotes = load("quotes.json", {}).get("quotes", {})
    bias_doc = load("commodity_bias.json", {"biases": [], "macro": ""})
    bias_by_material = {b["material"]: b for b in bias_doc.get("biases", [])}
    recs_doc = load("recommendations.json", {"recommendations": [], "tradeList": [], "sizing": ""})
    rec_by_ticker = {r["ticker"]: r for r in recs_doc.get("recommendations", [])}
    discoveries = load("discoveries.json", {"discoveries": []})["discoveries"]
    funda = load("fundamentals.json", {"fundamentals": {}})["fundamentals"]
    sweep = load("tipranks_sweep.json", {"analyst": {}, "sentiment": {}})
    sweep_analyst, sweep_sent = sweep.get("analyst", {}), sweep.get("sentiment", {})

    deep = {}
    for f in sorted(glob.glob(str(SRC / "deep_*.json"))):
        doc = json.loads(pathlib.Path(f).read_text())
        for n in doc.get("names", []):
            deep[n["ticker"]] = n

    # AI Hedge Fund layer: yahoo.json (Yahoo cross-val source) + hedge_*.json verdicts.
    # hedge_auto.json (deterministic fallback) sorts first, so any live hedge_r*.json
    # research shard overwrites it — same load-order trick as deep_auto vs deep_r*.
    yahoo = load("yahoo.json", {"quotes": {}}).get("quotes", {})
    hedge = {}
    for f in sorted(glob.glob(str(SRC / "hedge_*.json"))):
        doc = json.loads(pathlib.Path(f).read_text())
        for n in doc.get("names", []):
            hedge[n["ticker"]] = n

    out_tickers = []
    for rec in universe["tickers"]:
        if rec.get("excluded"):
            continue
        t = rec["ticker"]
        q = quotes.get(t)
        d = deep.get(t)
        f = funda.get(t)
        # live TipRanks sweep refresh takes precedence over the Excel snapshot
        if t in sweep_analyst and not (d and d.get("analyst") and d["analyst"].get("priceTarget")):
            d = dict(d) if d else {}
            d["analyst"] = {**(d.get("analyst") or {}), **sweep_analyst[t]}
        if t in sweep_sent:
            rec = dict(rec)
            tr0 = dict(rec.get("tipranks") or {})
            if sweep_sent[t].get("smartScore") is not None:
                tr0["smartScore"] = sweep_sent[t]["smartScore"]
            if sweep_sent[t].get("newsSentiment"):
                tr0["newsSentiment"] = sweep_sent[t]["newsSentiment"]
            rec["tipranks"] = tr0
        subs = {
            "momentum": momentum_score(q),
            "commodity": commodity_score(rec, bias_by_material),
            "deep": float(d["microScore"]) if d and d.get("microScore") is not None else None,
            "analyst": analyst_score(rec, d),
            "fundamentals": fundamentals_score(f),
            "smart": smart_score(rec, d),
            "sentiment": sentiment_score(rec),
            "quality": quality_score(rec, q),
        }
        composite, coverage = composite_from_subs(subs)
        if composite is None:
            continue

        # full analyst snapshot: deep-dive refresh first, Excel TipRanks as fallback
        tr = rec.get("tipranks") or {}
        analyst = dict(d["analyst"]) if d and d.get("analyst") else {}
        for src_key, dst_key in (("consensus", "consensus"), ("priceTarget", "priceTarget"),
                                 ("upside", "upsidePct"), ("buy", "buys"), ("hold", "holds"),
                                 ("sell", "sells"), ("analysts", "analysts")):
            if analyst.get(dst_key) is None and tr.get(src_key) is not None:
                analyst[dst_key] = tr.get(src_key)
        if analyst.get("smartScore") is None and tr.get("smartScore") is not None:
            analyst["smartScore"] = tr.get("smartScore")

        reco = rec_by_ticker.get(t)
        out_tickers.append({
            "ticker": t,
            "company": rec.get("company"),
            "material": (rec.get("materials") or [None])[0],
            "role": rec.get("role"),
            "capTier": rec.get("capTier"),
            "held": rec["held"]["side"] if rec.get("held") else None,
            "heldMv": rec["held"]["mktValue"] if rec.get("held") else None,
            "position": rec.get("held"),
            "country": rec.get("country"),
            "exchange": rec.get("exchange") or (q.get("exchange") if q else None),
            "analyst": analyst or None,
            "tipranksExtra": {k: tr.get(k) for k in
                              ("newsSentiment", "newsScore", "newsBuzz", "hedgeFundTrend",
                               "insiderTrend", "blogger") if tr.get(k) is not None} or None,
            "recommendation": ({"action": reco["action"], "urgency": reco.get("urgency"),
                                "rationale": reco["rationale"]} if reco else None),
            "price": q.get("price") if q else None,
            "vs50": q.get("vs50") if q else None,
            "vs200": q.get("vs200") if q else None,
            "range52w": q.get("range52w") if q else None,
            "marketCap": q.get("marketCap") if q else None,
            "tradable": tradable(rec, q),
            "quoteSuspect": bool(q and q.get("suspect")),
            "composite": composite,
            "subs": {k: (round(v, 1) if v is not None else None) for k, v in subs.items()},
            "coverage": coverage,
            "microVerdict": d.get("microVerdict") if d else None,
            "thesis": d.get("thesis") if d else None,
            "catalysts": d.get("catalysts", []) if d else [],
            "risks": d.get("risks", []) if d else [],
            "evidence": d.get("evidence", []) if d else [],
            "deepModelDerived": bool(d.get("modelDerived")) if d else False,
            "omLinkage": rec["omLinkage"]["score"] if rec.get("omLinkage") else None,
            "omEvidence": (rec["omLinkage"].get("evidence") if rec.get("omLinkage") else None)
                          or (rec["bigdata"].get("evidence") if rec.get("bigdata") else None),
            "exposure": ({
                "commodity": rec["omLinkage"].get("commodity"),
                "exposure": rec["omLinkage"].get("exposure"),
                "priceSens": rec["omLinkage"].get("priceSens"),
                "coupling": rec["omLinkage"].get("coupling"),
                "score": rec["omLinkage"].get("score"),
                "tier": rec["omLinkage"].get("tier"),
                "confidence": rec["omLinkage"].get("confidence"),
                "evidence": rec["omLinkage"].get("evidence"),
            } if rec.get("omLinkage") else None),
            "fundamentals": f,
            "hedgeFund": hedge_block(hedge.get(t)),
            "hedgeCrossVal": cross_validation(analyst, f, q.get("price") if q else None, yahoo.get(t)),
            "discovered": rec.get("discovered", False),
        })

    # discovered names (not in the Excel universe) get quote-only rows
    known = {r["ticker"] for r in out_tickers}
    for disc in discoveries:
        if disc["ticker"] in known:
            continue
        q = {"vs50": disc.get("vs50"), "vs200": disc.get("vs200"), "price": disc.get("price"),
             "marketCap": disc.get("marketCap")}
        mom = momentum_score(q)
        disc_reco = rec_by_ticker.get(disc["ticker"])
        disc_deep = deep.get(disc["ticker"])
        out_tickers.append({
            "ticker": disc["ticker"], "company": disc.get("company"),
            "material": disc.get("material"), "role": disc.get("role"), "capTier": None,
            "held": None, "heldMv": None, "position": None,
            "country": None, "exchange": disc.get("exchange"),
            "analyst": disc_deep.get("analyst") if disc_deep else None,
            "tipranksExtra": None,
            "recommendation": ({"action": disc_reco["action"], "urgency": disc_reco.get("urgency"),
                                "rationale": disc_reco["rationale"]} if disc_reco else None),
            "omEvidence": None,
            "price": disc.get("price"), "vs50": disc.get("vs50"), "vs200": disc.get("vs200"),
            "range52w": None, "marketCap": disc.get("marketCap"),
            "tradable": True, "quoteSuspect": False,
            "composite": (round((mom + float(disc_deep["microScore"])) / 2 * 10, 1)
                          if mom is not None and disc_deep and disc_deep.get("microScore") is not None
                          else round(mom, 1) * 10 if mom is not None else None),
            "subs": {"momentum": round(mom, 1) if mom is not None else None,
                     "deep": float(disc_deep["microScore"]) if disc_deep and disc_deep.get("microScore") is not None else None},
            "coverage": 35 if disc_deep else 20,
            "microVerdict": disc_deep.get("microVerdict") if disc_deep else None,
            "thesis": (disc_deep.get("thesis") if disc_deep else None) or disc.get("whyRelevant"),
            "catalysts": disc_deep.get("catalysts", []) if disc_deep else [],
            "risks": disc_deep.get("risks", []) if disc_deep else [],
            "evidence": disc_deep.get("evidence", []) if disc_deep else [],
            "omLinkage": None, "exposure": None,
            "fundamentals": funda.get(disc["ticker"]),
            "hedgeFund": hedge_block(hedge.get(disc["ticker"])),
            "hedgeCrossVal": cross_validation(disc_deep.get("analyst") if disc_deep else None,
                                              funda.get(disc["ticker"]), disc.get("price"),
                                              yahoo.get(disc["ticker"])),
            "discovered": True,
        })
        if out_tickers[-1]["fundamentals"]:
            fs = fundamentals_score(out_tickers[-1]["fundamentals"])
            if fs is not None:
                out_tickers[-1]["subs"]["fundamentals"] = fs

    # rank within material group (tradable names only get ranks)
    rank_within_groups(out_tickers)

    out_tickers.sort(key=lambda r: (-(r["composite"] or -1)))

    _now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    out = {
        "updatedAt": _now,
        "researchAsOf": _now,   # full MCP research build time; micro_refresh.py bumps only pricesRefreshedAt
        "methodology": ("Composite 0-100 = momentum 18% + commodity-alignment 18% + deep-dive 14% "
                        "+ analyst 13% + fundamentals 12% + news sentiment 9% + SmartScore 8% + quality 8% "
                        "(missing sub-scores redistribute). High = long candidate, low = short candidate. "
                        "Each card also carries an AI Hedge Fund multi-analyst verdict (4 analytical + "
                        "investor-persona lenses + a risk/portfolio-manager aggregate; concept ported from "
                        "virattt/ai-hedge-fund, MIT) plus an independent Yahoo Finance (yfinance) "
                        "cross-validation of price targets, ratings and margins. The hedge-fund layer is "
                        "display-only and does not change the composite. "
                        "Sources: IBKR, FMP, TipRanks, Bigdata.com (RavenPack), Carbon Arc, MetalMiner, TrueNorth, Yahoo Finance."),
        "macro": bias_doc.get("macro", ""),
        "commodityBias": [
            {"material": b["material"], "bias": b["bias"], "score": b["score"],
             "confidence": b["confidence"], "evidence": b["evidence"]}
            for b in bias_doc.get("biases", [])
        ],
        "tickers": out_tickers,
        "recommendations": recs_doc.get("recommendations", []),
        "tradeList": recs_doc.get("tradeList", []),
        "sizingNote": recs_doc.get("sizing", ""),
    }
    (DATA / "micro.json").write_text(json.dumps(out, indent=1))
    held = [r for r in out_tickers if r["held"]]
    print(f"micro.json: {len(out_tickers)} scored ({len(held)} held, "
          f"{sum(1 for r in out_tickers if r['discovered'])} discovered), "
          f"{len(out['recommendations'])} recommendations")


if __name__ == "__main__":
    main()
