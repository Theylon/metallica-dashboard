#!/usr/bin/env python3
"""Channel accuracy engine — which data channels have earned the right to drive decisions?

Backtests every information channel the process consumes against the thing it
claims to predict, and writes data/channel_accuracy.json for the Process tab:

  kpi.consensus.<TKR>  — street consensus vs reported KPI (altdata trackRecord).
                         Median Absolute Error over the tracked quarters →
                         accuracyPct = 100 − MedAE.
  kpi.ourEst.<TKR>     — our own nowcast vs reported, same math, plus
                         beatConsensusPct (share of quarters we were closer to
                         reported than the street). Only exists once altdata
                         Phase 2 calibrations fill kpi.ourEst.
  score.<sub>          — each micro sub-score + composite vs forward returns,
                         straight from signal_scorecard.json (rank-IC hit rate).
  direction.commodityBias / .insider / .politician
                       — directional calls (long/short, buying/selling) vs the
                         20-snapshot-forward return of the named ticker.
  crossval.yahoo       — source consistency (Yahoo vs FMP/TipRanks cross-check);
                         informational, never gated.

The gate: a channel is "trusted" only when its accuracyPct clears
GATE["trustedMinPct"] (80%) on enough observations; measured-but-below is
"probation" (display-only, not a decision input — see PROCESS.md); not enough
history yet is "accumulating". Pure stdlib, reads only committed data/ files →
runs in the GitHub Action.
"""
import datetime
import json
import pathlib
import statistics

DATA = pathlib.Path(__file__).resolve().parent.parent / "data"

GATE = {"trustedMinPct": 80}
MIN_N = {"kpi": 2, "score": 5, "direction": 10}   # min observations before the gate applies
FWD_SNAPSHOTS = 20                                 # forward horizon for direction channels
MIN_DATES = FWD_SNAPSHOTS + 5                      # snapshot days before direction channels turn on


def _load(name, default):
    p = DATA / name
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text())
    except Exception:
        return default


def _load_jsonl(name):
    p = DATA / name
    if not p.exists():
        return []
    rows = []
    for line in p.read_text().splitlines():
        if line.strip():
            try:
                rows.append(json.loads(line))
            except Exception:
                pass
    return rows


def channel(id_, label, kind, **kw):
    base = {"id": id_, "label": label, "kind": kind, "source": "", "ticker": None,
            "n": 0, "medAbsErrPct": None, "meanAbsErrPct": None,
            "beatConsensusPct": None, "hitRatePct": None,
            "accuracyPct": None, "status": "accumulating", "gated": True,
            "note": None, "detail": []}
    base.update(kw)
    return base


def _gate(ch):
    """Apply the trust gate in place (skipped for informational channels)."""
    if not ch["gated"]:
        ch["status"] = "info"
        return ch
    n_min = MIN_N.get(ch["kind"], 2)
    if ch["accuracyPct"] is None or ch["n"] < n_min:
        ch["status"] = "accumulating"
    elif ch["accuracyPct"] >= GATE["trustedMinPct"]:
        ch["status"] = "trusted"
    else:
        ch["status"] = "probation"
    return ch


# ── KPI channels (altdata trackRecord) ────────────────────────────────────────
def kpi_channels(altdata):
    out = []
    any_ourest = False
    for it in altdata.get("items", []):
        tkr = it.get("ticker")
        kpi_name = ((it.get("kpi") or {}).get("name")) or "KPI"
        rows = [r for r in it.get("trackRecord") or []
                if r.get("reported") not in (None, 0)]

        cons_errs, detail = [], []
        for r in rows:
            if r.get("consensus") is None:
                continue
            err = (abs(r["deltaToReported"]) if r.get("deltaToReported") is not None
                   else abs(r["consensus"] / r["reported"] - 1) * 100)
            cons_errs.append(err)
            detail.append({"period": r.get("period"), "est": r.get("consensus"),
                           "reported": r.get("reported"), "absErrPct": round(err, 2)})
        if cons_errs:
            med = statistics.median(cons_errs)
            out.append(_gate(channel(
                f"kpi.consensus.{tkr}", f"Street consensus — {tkr} {kpi_name}", "kpi",
                source="FMP consensus vs reported (altdata trackRecord)", ticker=tkr,
                n=len(cons_errs), medAbsErrPct=round(med, 2),
                meanAbsErrPct=round(sum(cons_errs) / len(cons_errs), 2),
                accuracyPct=round(max(0.0, 100 - med), 1), detail=detail)))

        our_errs, our_detail, beats, paired = [], [], 0, 0
        for r in rows:
            if r.get("ourEst") is None:
                continue
            err = abs(r["ourEst"] / r["reported"] - 1) * 100
            our_errs.append(err)
            our_detail.append({"period": r.get("period"), "est": r.get("ourEst"),
                               "reported": r.get("reported"), "absErrPct": round(err, 2)})
            if r.get("consensus") is not None:
                paired += 1
                if err < abs(r["consensus"] / r["reported"] - 1) * 100:
                    beats += 1
        if our_errs:
            any_ourest = True
            med = statistics.median(our_errs)
            out.append(_gate(channel(
                f"kpi.ourEst.{tkr}", f"Our nowcast — {tkr} {kpi_name}", "kpi",
                source="Alt-data calibrated estimate vs reported", ticker=tkr,
                n=len(our_errs), medAbsErrPct=round(med, 2),
                meanAbsErrPct=round(sum(our_errs) / len(our_errs), 2),
                beatConsensusPct=round(beats / paired * 100, 1) if paired else None,
                accuracyPct=round(max(0.0, 100 - med), 1), detail=our_detail)))

    if not any_ourest:
        out.append(channel(
            "kpi.ourEst", "Our nowcast — all names", "kpi",
            source="Alt-data calibrated estimate vs reported",
            note="No calibrated nowcasts yet — fills once altdata Phase 2 sets kpi.ourEst "
                 "(needs ≥2 quarters of paired alt-data ↔ reported history per name)."))
    return out


# ── score channels (signal_scorecard) ─────────────────────────────────────────
def score_channels(scorecard):
    if scorecard.get("status") != "ready" or not scorecard.get("signals"):
        days = scorecard.get("daysCollected", 0)
        need = scorecard.get("minDaysNeeded", 25)
        return [channel(
            "score.microScores", "Micro sub-scores + composite vs forward returns", "score",
            source="signal_scorecard.json (rank-IC engine)",
            note=f"needs {need} daily snapshots ({days} so far)")]
    out = []
    for s in scorecard["signals"]:
        hit = s.get("hitRate")
        out.append(_gate(channel(
            f"score.{s['signal']}", f"{s['signal'].capitalize()} score vs forward returns",
            "score", source="signal_scorecard.json (rank-IC engine)",
            n=s.get("windows", 0),
            hitRatePct=round(hit * 100, 1) if hit is not None else None,
            accuracyPct=round(hit * 100, 1) if hit is not None else None,
            detail=[{"rankIC": s.get("rankIC"), "IR": s.get("IR"),
                     "tstat": s.get("ic_tstat"), "obs": s.get("n")}])))
    return out


# ── direction channels ────────────────────────────────────────────────────────
def _dir_hits(calls, price_by_date, dates):
    """calls: [(date, ticker, 'long'|'short'|'bullish'|'bearish')] → (hits, n)."""
    idx = {d: i for i, d in enumerate(dates)}
    hits = n = 0
    for date, ticker, direction in calls:
        i = idx.get(date)
        if i is None or i + FWD_SNAPSHOTS >= len(dates):
            continue
        a = price_by_date.get(date, {}).get(ticker)
        b = price_by_date.get(dates[i + FWD_SNAPSHOTS], {}).get(ticker)
        if not a or not b:
            continue
        fwd = b / a - 1
        want_up = direction in ("long", "bullish")
        n += 1
        if (fwd > 0) == want_up:
            hits += 1
    return hits, n


def direction_channels(history_rows, positioning_rows):
    price_by_date, bias_calls = {}, []
    for r in history_rows:
        price_by_date.setdefault(r["date"], {})[r["ticker"]] = r.get("priceAnchor")
        if r.get("biasDir") in ("long", "short"):
            bias_calls.append((r["date"], r["ticker"], r["biasDir"]))
    dates = sorted(price_by_date)

    out = []

    def add(id_, label, source, calls, note_when_empty):
        if len(dates) >= MIN_DATES and calls:
            hits, n = _dir_hits(calls, price_by_date, dates)
        else:
            hits, n = 0, 0
        ch = channel(id_, label, "direction", source=source, n=n,
                     hitRatePct=round(hits / n * 100, 1) if n else None,
                     accuracyPct=round(hits / n * 100, 1) if n else None)
        if not n:
            ch["note"] = note_when_empty
        out.append(_gate(ch))

    add("direction.commodityBias", "Commodity bias (long/short per material)",
        "micro_history.jsonl biasDir vs 20-snapshot-forward return", bias_calls,
        f"needs ≥{MIN_DATES} snapshot days with biasDir recorded "
        f"({len(dates)} days so far, {len(bias_calls)} directional rows)")

    for chan, label in (("insider", "Insider buys/sells (discretionary only)"),
                        ("politician", "Politician / congressional trades")):
        calls = [(r["date"], r["ticker"], r["signal"])
                 for r in positioning_rows
                 if r.get("channel") == chan and r.get("signal") in ("bullish", "bearish")]
        add(f"direction.{chan}", label,
            "positioning_history.jsonl vs 20-snapshot-forward return", calls,
            f"needs ≥{MIN_N['direction']} aged observations "
            f"({len(calls)} directional rows so far)")
    return out


# ── cross-validation (informational) ──────────────────────────────────────────
def crossval_channel(micro):
    counts = {"agree": 0, "mixed": 0, "conflict": 0}
    for r in micro.get("tickers", []):
        a = (r.get("crossVal") or {}).get("agreement")
        if a in counts:
            counts[a] += 1
    total = sum(counts.values())
    ch = channel("crossval.yahoo", "Source consistency — Yahoo vs FMP/TipRanks",
                 "crossval", source="micro.json crossVal (independent yfinance pull)",
                 gated=False, n=total,
                 accuracyPct=round(counts["agree"] / total * 100, 1) if total else None,
                 detail=[counts])
    if not total:
        ch["note"] = "no cross-validated names yet"
    return _gate(ch)


# ── assemble ──────────────────────────────────────────────────────────────────
_STATUS_ORDER = {"trusted": 0, "probation": 1, "accumulating": 2, "info": 3}


def build():
    altdata = _load("altdata.json", {"items": []})
    scorecard = _load("signal_scorecard.json", {})
    micro = _load("micro.json", {"tickers": []})
    history = _load_jsonl("micro_history.jsonl")
    positioning = _load_jsonl("positioning_history.jsonl")

    channels = (kpi_channels(altdata) + score_channels(scorecard)
                + direction_channels(history, positioning) + [crossval_channel(micro)])
    channels.sort(key=lambda c: (_STATUS_ORDER.get(c["status"], 9),
                                 -(c["accuracyPct"] or 0), c["id"]))
    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    return {
        "updatedAt": now,
        "gate": GATE,
        "summary": {
            "trusted": sum(1 for c in channels if c["status"] == "trusted"),
            "probation": sum(1 for c in channels if c["status"] == "probation"),
            "accumulating": sum(1 for c in channels if c["status"] == "accumulating"),
        },
        "channels": channels,
    }


def write():
    doc = build()
    (DATA / "channel_accuracy.json").write_text(json.dumps(doc, indent=1) + "\n")
    return doc


if __name__ == "__main__":
    doc = write()
    s = doc["summary"]
    print(f"channel_accuracy.json: {len(doc['channels'])} channels "
          f"({s['trusted']} trusted, {s['probation']} probation, {s['accumulating']} accumulating)")
