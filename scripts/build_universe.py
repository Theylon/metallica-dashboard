#!/usr/bin/env python3
"""Build data/universe.json from the MetalMiner materials→stocks Excel map.

Usage: python3 scripts/build_universe.py <path-to-mm_materials_stock_map_enriched.xlsx>

Merges the Excel sheets (master list, OM linkage, TipRanks enrichment, Bigdata
enrichment) into one record per ticker, then overlays live held positions from
data/positions.json. micro_build.py consumes this file as its scoring input.
"""
import json
import math
import pathlib
import sys

import pandas as pd

DATA = pathlib.Path(__file__).resolve().parent.parent / "data"


def clean(v):
    if v is None:
        return None
    if isinstance(v, float) and math.isnan(v):
        return None
    if isinstance(v, str):
        v = v.strip()
        return v if v and v != "-" else None
    return v


def row_dict(row, mapping):
    return {out: clean(row.get(src)) for src, out in mapping.items()}


def main(xlsx_path):
    xl = pd.ExcelFile(xlsx_path)
    mm = xl.parse("MM Materials-Stocks")
    om = xl.parse("OM Linkage (Bigdata)")
    tr = xl.parse("TipRanks Enrichment")
    bd = xl.parse("Bigdata Enrichment")
    tier1 = xl.parse("Tier-1 Distilled")

    om_by_ticker = {clean(r["Ticker"]): r for _, r in om.iterrows()}
    tr_by_ticker = {clean(r["Ticker"]): r for _, r in tr.iterrows()}
    bd_by_ticker = {clean(r["Ticker"]): r for _, r in bd.iterrows()}
    tier1_ranks = {clean(r["Ticker"]): int(r["Rank"]) for _, r in tier1.iterrows()
                   if clean(r["Ticker"]) and clean(r["Rank"]) is not None}

    held = {}
    pos_file = DATA / "positions.json"
    if pos_file.exists():
        for p in json.loads(pos_file.read_text())["positions"]:
            t = p["ticker"].split(" @")[0]  # "IMPUY @PINK" -> "IMPUY"
            held[t] = {
                "side": p["side"],
                "shares": p["shares"],
                "mktValue": p["mktValue"],
                "unrealizedPnl": p["unrealizedPnl"],
                "avgCost": p["avgCost"],
                "lastPrice": p["lastPrice"],
            }

    records = {}
    for _, row in mm.iterrows():
        ticker = clean(row["Ticker"])
        if not ticker:
            continue
        material = clean(row["Material"])
        status = clean(row["Status"])
        verified = clean(row["Verified"])
        if ticker in records:
            mats = records[ticker]["materials"]
            if material and material not in mats:
                mats.append(material)
            continue

        omr = om_by_ticker.get(ticker)
        trr = tr_by_ticker.get(ticker)
        bdr = bd_by_ticker.get(ticker)

        rec = {
            "ticker": ticker,
            "company": clean(row["Company"]),
            "materials": [material] if material else [],
            "country": clean(row["Country"]),
            "region": clean(row["Region"]),
            "exchange": clean(row["Primary Exchange"]),
            "capTier": clean(row["Cap Tier (approx)"]),
            "role": clean(row["Role"]),
            "status": status,
            "verified": verified,
            "sources": int(row["Sources"]) if clean(row.get("Sources")) is not None else 0,
            "excluded": not (verified == "Y" and status not in ("delisted/acquired", "not-public", "duplicate")),
            "tier1Rank": tier1_ranks.get(ticker),
            "omLinkage": None,
            "tipranks": None,
            "bigdata": None,
            "held": held.get(ticker),
            "discovered": False,
        }
        if omr is not None:
            rec["omLinkage"] = row_dict(omr, {
                "Commodity": "commodity", "Role": "role", "Exposure": "exposure",
                "PriceSens": "priceSens", "Coupling": "coupling",
                "Linkage(0-9)": "score", "Tier": "tier", "Confidence": "confidence",
                "Evidence (Bigdata)": "evidence",
            })
        if trr is not None:
            rec["tipranks"] = row_dict(trr, {
                "TR Consensus": "consensus", "Buy": "buy", "Hold": "hold", "Sell": "sell",
                "# Analysts": "analysts", "Avg Price Target": "priceTarget",
                "Upside %": "upside", "Covered": "covered", "Note": "note",
                "News Sentiment": "newsSentiment", "News Score(0-1)": "newsScore",
                "News Buzz": "newsBuzz",
            })
            # SmartScore & trend columns live on the master sheet
            rec["tipranks"].update(row_dict(row, {
                "TR SmartScore": "smartScore", "TR News Sentiment": "newsSentimentMM",
                "TR HedgeFund Trend": "hedgeFundTrend", "TR Insider Trend": "insiderTrend",
                "TR Blogger": "blogger",
            }))
        if bdr is not None:
            rec["bigdata"] = row_dict(bdr, {
                "Role": "role", "PriceSens(0-3)": "priceSens", "Confidence": "confidence",
                "Suggested Status": "suggestedStatus",
                "Evidence (Bigdata)": "evidence",
            })
        records[ticker] = rec

    # held positions not present in the Excel map (e.g. new buys) get stub rows
    for t, h in held.items():
        if t not in records:
            records[t] = {
                "ticker": t, "company": t, "materials": [], "country": None,
                "region": None, "exchange": None, "capTier": None, "role": None,
                "status": "held-only", "verified": None, "sources": 0,
                "excluded": False, "tier1Rank": None, "omLinkage": None,
                "tipranks": None, "bigdata": None, "held": h, "discovered": False,
            }

    out = {
        "updatedAt": json.loads((DATA / "account.json").read_text()).get("updatedAt"),
        "source": pathlib.Path(xlsx_path).name,
        "count": len(records),
        "tickers": sorted(records.values(), key=lambda r: (r["materials"][0] if r["materials"] else "zz", r["ticker"])),
    }
    (DATA / "universe.json").write_text(json.dumps(out, indent=1))
    n_ok = sum(1 for r in records.values() if not r["excluded"])
    n_held = sum(1 for r in records.values() if r["held"])
    print(f"universe.json: {len(records)} tickers ({n_ok} scoreable, {n_held} held)")


if __name__ == "__main__":
    main(sys.argv[1])
