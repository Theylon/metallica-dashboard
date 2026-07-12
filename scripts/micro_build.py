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

DATA = pathlib.Path(__file__).resolve().parent.parent / "data"
SRC = pathlib.Path(os.environ.get(
    "MICRO_SRC",
    "/tmp/claude-0/-home-user-metallica-dashboard/a09c6b1b-2269-59e4-b962-3c7699dcd40f/scratchpad"))

WEIGHTS = {
    "momentum": 0.20, "commodity": 0.20, "deep": 0.15, "analyst": 0.15,
    "smart": 0.10, "sentiment": 0.10, "quality": 0.10,
}

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


def clamp(v, lo=0.0, hi=10.0):
    return max(lo, min(hi, v))


def load(name, default):
    p = SRC / name
    if p.exists():
        return json.loads(p.read_text())
    return default


def momentum_score(q):
    if not q or q.get("suspect"):
        return None
    s = 5.0
    if q.get("vs50") is not None:
        s += clamp(q["vs50"] / 6.0, -2.5, 2.5)      # ±15% vs 50DMA saturates
    if q.get("vs200") is not None:
        s += clamp(q["vs200"] / 12.0, -2.5, 2.5)    # ±30% vs 200DMA saturates
    if q.get("range52w") is not None:
        s += (q["range52w"] - 50.0) / 25.0          # 52w-range position, ±2
    return clamp(s)


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
    for key in ("newsSentiment", "newsSentimentMM"):
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


def tradable(rec, q):
    ex = (rec.get("exchange") or (q.get("exchange") if q else "") or "")
    us = any(k in str(ex).upper() for k in ("NYSE", "NASDAQ", "AMEX", "ADR", "CBOE", "OTC"))
    liquid = bool(q) and not q.get("suspect") and (q.get("marketCap") or 0) > 1.5e8 and (q.get("price") or 0) >= 1
    return us and liquid


def main():
    universe = json.loads((DATA / "universe.json").read_text())
    quotes = load("quotes.json", {}).get("quotes", {})
    bias_doc = load("commodity_bias.json", {"biases": [], "macro": ""})
    bias_by_material = {b["material"]: b for b in bias_doc.get("biases", [])}
    recs_doc = load("recommendations.json", {"recommendations": [], "tradeList": [], "sizing": ""})
    rec_by_ticker = {r["ticker"]: r for r in recs_doc.get("recommendations", [])}
    discoveries = load("discoveries.json", {"discoveries": []})["discoveries"]

    deep = {}
    for f in sorted(glob.glob(str(SRC / "deep_*.json"))):
        doc = json.loads(pathlib.Path(f).read_text())
        for n in doc.get("names", []):
            deep[n["ticker"]] = n

    out_tickers = []
    for rec in universe["tickers"]:
        if rec.get("excluded"):
            continue
        t = rec["ticker"]
        q = quotes.get(t)
        d = deep.get(t)
        subs = {
            "momentum": momentum_score(q),
            "commodity": commodity_score(rec, bias_by_material),
            "deep": float(d["microScore"]) if d and d.get("microScore") is not None else None,
            "analyst": analyst_score(rec, d),
            "smart": smart_score(rec, d),
            "sentiment": sentiment_score(rec),
            "quality": quality_score(rec, q),
        }
        avail = {k: v for k, v in subs.items() if v is not None}
        if not avail:
            continue
        wsum = sum(WEIGHTS[k] for k in avail)
        composite = sum(WEIGHTS[k] * v for k, v in avail.items()) / wsum * 10.0

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
            "composite": round(composite, 1),
            "subs": {k: (round(v, 1) if v is not None else None) for k, v in subs.items()},
            "coverage": round(wsum / sum(WEIGHTS.values()) * 100),
            "microVerdict": d.get("microVerdict") if d else None,
            "thesis": d.get("thesis") if d else None,
            "catalysts": d.get("catalysts", []) if d else [],
            "risks": d.get("risks", []) if d else [],
            "evidence": d.get("evidence", []) if d else [],
            "omLinkage": rec["omLinkage"]["score"] if rec.get("omLinkage") else None,
            "omEvidence": (rec["omLinkage"].get("evidence") if rec.get("omLinkage") else None)
                          or (rec["bigdata"].get("evidence") if rec.get("bigdata") else None),
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
            "omLinkage": None, "discovered": True,
        })

    # rank within material group (tradable names only get ranks)
    by_mat = {}
    for r in out_tickers:
        if r["composite"] is not None and r["tradable"]:
            by_mat.setdefault(r["material"], []).append(r)
    for mat, rows in by_mat.items():
        rows.sort(key=lambda r: -r["composite"])
        for i, r in enumerate(rows, 1):
            r["groupRank"] = f"{i}/{len(rows)}"

    out_tickers.sort(key=lambda r: (-(r["composite"] or -1)))

    out = {
        "updatedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "methodology": ("Composite 0-100 = momentum 20% + commodity-alignment 20% + deep-dive 15% "
                        "+ analyst 15% + TipRanks SmartScore 10% + news sentiment 10% + quality 10% "
                        "(missing sub-scores redistribute). High = long candidate, low = short candidate. "
                        "Sources: IBKR, FMP, TipRanks, Bigdata.com (RavenPack), Carbon Arc, MetalMiner."),
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
