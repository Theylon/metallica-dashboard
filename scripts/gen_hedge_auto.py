#!/usr/bin/env python3
"""Generate a data-grounded AI-Hedge-Fund verdict for every universe name.

Ports the multi-analyst idea of virattt/ai-hedge-fund (MIT) into this pipeline as a
DETERMINISTIC fallback: a full roster of investor-persona + analytical lenses, each
emitting a signal (bullish/bearish/neutral) + confidence (0-100) + one-line reasoning,
plus a Portfolio-Manager aggregate. No upstream code is copied and NO LLM/API key is
used — every lens is a tilt over signals already in the pipeline (commodity bias, OM
linkage, momentum, analyst snapshot, TrueNorth fundamentals), reusing the exact
sub-score helpers in micro_build/micro_score so it can't drift from the composite.

A daily Claude Routine can overwrite any name with a researched verdict by dropping
`hedge_r*.json` shards next to this file; micro_build.py merges all `hedge_*.json` by
glob and `hedge_auto.json` sorts first, so research shards always win (identical to how
`deep_auto.json` backstops the deep dives). Rebuilds therefore always yield a valid,
fully-populated hedgeFund layer even with no live research run.

Output: data/micro_src/hedge_auto.json — consumed by micro_build.py.
"""
import datetime
import json
import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from micro_score import clamp, momentum_score
from micro_build import (analyst_score, commodity_score, fundamentals_score,
                         quality_score, sentiment_score, smart_score, tradable)

DATA = pathlib.Path(__file__).resolve().parent.parent / "data"
SRC = pathlib.Path(os.environ.get("MICRO_SRC", str(DATA / "micro_src")))

# Full roster (concept ported from virattt/ai-hedge-fund, MIT). Portfolio Manager is
# emitted as the `aggregate`, so it is named in the roster but not in `analysts[]`.
ROSTER = ["Valuation", "Fundamentals", "Technicals", "Sentiment",
          "Warren Buffett", "Charlie Munger", "Ben Graham", "Cathie Wood",
          "Bill Ackman", "Peter Lynch", "Michael Burry", "Stanley Druckenmiller",
          "Phil Fisher", "Risk Manager", "Portfolio Manager"]

BULL, BEAR = 6.3, 4.0   # same thresholds as gen_deep_auto's verdict cut


def load(name, default):
    p = SRC / name
    return json.loads(p.read_text()) if p.exists() else default


def avg(*vals):
    xs = [v for v in vals if v is not None]
    return sum(xs) / len(xs) if xs else None


def sig_of(lean):
    if lean is None:
        return "neutral"
    return "bullish" if lean >= BULL else "bearish" if lean <= BEAR else "neutral"


def conf_of(lean, floor=25, cap=92, scale=15):
    """Conviction rises with distance from the neutral midpoint (5.0)."""
    if lean is None:
        return floor
    return int(round(max(floor, min(cap, abs(lean - 5.0) * scale + 30))))


def fund_components(f):
    """Decompose TrueNorth annual metrics into 0-10 lenses (mirrors fundamentals_score)."""
    if not f:
        return {}
    c = {}
    if f.get("ebitda_margin") is not None:
        c["margin"] = clamp(f["ebitda_margin"] * 25.0)                 # 40% margin = 10
    roic, roe = f.get("return_on_invested_capital"), f.get("return_on_equity")
    if roic is not None:
        c["roic"] = clamp(5.0 + roic * 25.0)                          # ROIC 20% = 10
    elif roe is not None:
        c["roic"] = clamp(5.0 + roe * 20.0)
    lev = []
    if f.get("net_debt_to_ebitda") is not None:
        lev.append(clamp(8.0 - 1.5 * max(0.0, f["net_debt_to_ebitda"])))
    if f.get("debt_to_equity") is not None:
        lev.append(clamp(9.0 - 4.0 * max(0.0, f["debt_to_equity"])))
    if lev:
        c["balance"] = sum(lev) / len(lev)
    g = [clamp(5.0 + f[k] * 10.0) for k in ("revenue_growth_yoy", "ebitda_growth_yoy")
         if f.get(k) is not None]
    if g:
        c["growth"] = sum(g) / len(g)
    if f.get("free_cash_flow_margin") is not None:
        c["fcf"] = clamp(5.0 + f["free_cash_flow_margin"] * 40.0)
    return c


def pct(v):
    return f"{v * 100:.0f}%" if isinstance(v, (int, float)) else "n/a"


def build_verdicts(subs, f, fc, mom_q, bias, role, linkage, is_tradable, suspect, upside):
    """Return (analysts[], aggregate) for one name from its already-computed signals."""
    mom = subs.get("momentum")
    contra = clamp(10.0 - mom) if mom is not None else None   # cheap/oversold proxy
    margin, roic, balance = fc.get("margin"), fc.get("roic"), fc.get("balance")
    growth, fcf = fc.get("growth"), fc.get("fcf")

    def r_mom():
        v50 = mom_q.get("vs50") if mom_q else None
        v200 = mom_q.get("vs200") if mom_q else None
        bits = [f"{'+' if x >= 0 else ''}{x:.0f}% vs {n}DMA"
                for x, n in ((v50, "50"), (v200, "200")) if x is not None]
        return ", ".join(bits) or "no price trend data"

    lenses = []  # (name, type, lean, reasoning)

    # ── Analytical agents ───────────────────────────────────────────────
    lenses.append(("Valuation", "analytical", subs.get("analyst"),
                   (f"Analyst target implies {upside:+.0f}% upside." if isinstance(upside, (int, float))
                    else "Valuation leans on the analyst snapshot; no clean target upside.")))
    lenses.append(("Fundamentals", "analytical", subs.get("fundamentals"),
                   (f"EBITDA margin {pct(f.get('ebitda_margin'))}, ROIC {pct(f.get('return_on_invested_capital'))}, "
                    f"net debt/EBITDA {f.get('net_debt_to_ebitda'):.1f}x." if f and f.get('net_debt_to_ebitda') is not None
                    else "Limited fundamentals coverage for this name.")))
    lenses.append(("Technicals", "analytical", mom, f"Price trend: {r_mom()}."))
    lenses.append(("Sentiment", "analytical", avg(subs.get("sentiment"), subs.get("smart")),
                   "News/SmartScore sentiment read from TipRanks."))

    # ── Investor personas ───────────────────────────────────────────────
    lenses.append(("Warren Buffett", "persona", avg(margin, roic, balance, subs.get("quality")),
                   (f"Wants a durable, low-debt compounder — margin {pct(f.get('ebitda_margin')) if f else 'n/a'}, "
                    f"ROIC {pct(f.get('return_on_invested_capital')) if f else 'n/a'}." )))
    lenses.append(("Charlie Munger", "persona", avg(roic, margin, subs.get("quality")),
                   "Concentrated quality: high returns on capital and a rational business."))
    lenses.append(("Ben Graham", "persona", avg(balance, contra, fcf),
                   "Margin of safety: strong balance sheet plus a beaten-down price."))
    lenses.append(("Cathie Wood", "persona", avg(growth, mom, growth),
                   (f"Growth/innovation: revenue growth {pct(f.get('revenue_growth_yoy')) if f else 'n/a'} and momentum.")))
    lenses.append(("Bill Ackman", "persona", avg(subs.get("quality"), margin, mom, subs.get("analyst")),
                   "Quality business with a catalyst and analyst support."))
    lenses.append(("Peter Lynch", "persona", avg(growth, subs.get("analyst"), subs.get("quality")),
                   "Growth at a reasonable price with a clear story."))
    lenses.append(("Michael Burry", "persona", avg(contra, balance, margin),
                   (f"Contrarian value: {'cheap/oversold' if (mom or 5) < 5 else 'extended — hard to be contrarian long'} "
                    "with a solid balance sheet.")))
    lenses.append(("Stanley Druckenmiller", "persona", avg(subs.get("commodity"), mom),
                   (f"Macro/commodity + tape: {bias['bias'].upper() if bias else 'neutral'} "
                    f"{'metal' if bias else 'backdrop'} bias, momentum aligned or not.")))
    lenses.append(("Phil Fisher", "persona", avg(growth, margin, subs.get("quality")),
                   "Scuttlebutt quality-growth: durable margins and reinvestment runway."))

    # ── Risk Manager ────────────────────────────────────────────────────
    risk_flags = []
    if not is_tradable:
        risk_flags.append("thin liquidity / hard to trade")
    if suspect:
        risk_flags.append("suspect quote")
    if f and f.get("net_debt_to_ebitda") is not None and f["net_debt_to_ebitda"] > 3.5:
        risk_flags.append("high leverage")
    if role in ("Explorer", "Developer"):
        risk_flags.append("pre-revenue")
    if risk_flags:
        risk_lean, risk_reason = 3.5, "Elevated risk: " + ", ".join(risk_flags) + "."
    elif balance is not None and balance >= 7 and (subs.get("quality") or 0) >= 7:
        risk_lean, risk_reason = 7.0, "Low risk: strong balance sheet and liquid quality name."
    else:
        risk_lean, risk_reason = 5.0, "Moderate, manageable risk profile."
    lenses.append(("Risk Manager", "manager", risk_lean, risk_reason))

    analysts = []
    for name, typ, lean, reason in lenses:
        analysts.append({"name": name, "type": typ, "signal": sig_of(lean),
                         "confidence": conf_of(lean), "reasoning": reason})

    # ── Portfolio Manager = aggregate (weighted tally of the lenses) ─────
    bull = sum(1 for a in analysts if a["signal"] == "bullish")
    bear = sum(1 for a in analysts if a["signal"] == "bearish")
    neu = sum(1 for a in analysts if a["signal"] == "neutral")
    total = max(1, len(analysts))
    signal = "bullish" if bull > bear else "bearish" if bear > bull else "neutral"
    agg_conf = int(round(min(90, 35 + abs(bull - bear) / total * 65)))
    if not is_tradable:
        agg_conf = min(agg_conf, 55)   # Risk-Manager down-weight for untradable names

    return analysts, {"signal": signal, "confidence": agg_conf,
                      "tally": {"bull": bull, "bear": bear, "neutral": neu}}


def action_for(signal, held):
    """Map the aggregate signal + current position side to a suggested action."""
    if held == "long":
        return {"bullish": "add", "bearish": "trim", "neutral": "hold"}[signal]
    if held == "short":
        return {"bullish": "cover", "bearish": "add", "neutral": "hold"}[signal]
    return {"bullish": "buy", "bearish": "short", "neutral": "watch"}[signal]


def context_for(rec, q, funda):
    """Compute the sub-scores + raw inputs one name needs, reusing micro_build helpers."""
    t = rec["ticker"]
    f = funda.get(t)
    subs = {
        "momentum": momentum_score(q),
        "commodity": commodity_score(rec, BIAS_BY_MATERIAL),
        "analyst": analyst_score(rec, None),
        "fundamentals": fundamentals_score(f),
        "smart": smart_score(rec, None),
        "sentiment": sentiment_score(rec),
        "quality": quality_score(rec, q),
    }
    mats = rec.get("materials") or []
    bias = BIAS_BY_MATERIAL.get(mats[0]) if mats else None
    om = rec.get("omLinkage") or {}
    tr = rec.get("tipranks") or {}
    # universe snapshots carry priceTarget but not a precomputed upside — derive it
    upside = tr.get("upside")
    price = q.get("price") if q else None
    if upside is None and tr.get("priceTarget") and price:
        try:
            upside = (float(tr["priceTarget"]) / float(price) - 1.0) * 100.0
        except (TypeError, ValueError, ZeroDivisionError):
            upside = None
    return {
        "subs": subs, "f": f, "fc": fund_components(f), "mom_q": q, "bias": bias,
        "role": rec.get("role"), "linkage": om.get("score"),
        "tradable": tradable(rec, q), "suspect": bool(q and q.get("suspect")),
        "upside": upside,
    }


def hedge_entry(rec, q, funda, today):
    ctx = context_for(rec, q, funda)
    analysts, aggregate = build_verdicts(
        ctx["subs"], ctx["f"], ctx["fc"], ctx["mom_q"], ctx["bias"], ctx["role"],
        ctx["linkage"], ctx["tradable"], ctx["suspect"], ctx["upside"])
    held = rec["held"]["side"] if rec.get("held") else None
    aggregate["action"] = action_for(aggregate["signal"], held)
    return {"ticker": rec["ticker"], "held": held, "aggregate": aggregate,
            "analysts": analysts, "modelDerived": True, "asOf": today}


def synth_rec(disc):
    """Build a minimal universe-shaped record for a discovered (non-Excel) name."""
    return {"ticker": disc["ticker"], "company": disc.get("company"),
            "materials": [disc["material"]] if disc.get("material") else [],
            "role": disc.get("role"), "capTier": None, "exchange": disc.get("exchange"),
            "omLinkage": None, "tipranks": {}, "held": None}


def main():
    universe = json.loads((DATA / "universe.json").read_text())["tickers"]
    quotes = load("quotes.json", {"quotes": {}})["quotes"]
    funda = load("fundamentals.json", {"fundamentals": {}})["fundamentals"]
    discoveries = load("discoveries.json", {"discoveries": []})["discoveries"]
    today = datetime.date.today().isoformat()

    names, seen = [], set()
    for rec in universe:
        if rec.get("excluded"):
            continue
        names.append(hedge_entry(rec, quotes.get(rec["ticker"]), funda, today))
        seen.add(rec["ticker"])
    for disc in discoveries:
        if disc["ticker"] in seen:
            continue
        q = {"price": disc.get("price"), "vs50": disc.get("vs50"),
             "vs200": disc.get("vs200"), "marketCap": disc.get("marketCap")}
        names.append(hedge_entry(synth_rec(disc), q, funda, today))
        seen.add(disc["ticker"])

    out = {
        "generatedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "generated": True,
        "roster": ROSTER,
        "note": ("Model-derived AI-Hedge-Fund verdicts (concept ported from "
                 "virattt/ai-hedge-fund, MIT). Each lens is a deterministic tilt over "
                 "signals already in the pipeline; not individually researched. A daily "
                 "Routine can overwrite any name via hedge_r*.json shards."),
        "names": names,
    }
    (SRC / "hedge_auto.json").write_text(json.dumps(out, indent=1))
    bull = sum(1 for n in names if n["aggregate"]["signal"] == "bullish")
    bear = sum(1 for n in names if n["aggregate"]["signal"] == "bearish")
    print(f"hedge_auto.json: {len(names)} names "
          f"({bull} bull / {bear} bear / {len(names) - bull - bear} neutral)")


# commodity_score needs the material→bias map; build it once at import for the helpers.
BIAS_BY_MATERIAL = {b["material"]: b for b in
                    load("commodity_bias.json", {"biases": []}).get("biases", [])}


if __name__ == "__main__":
    main()
