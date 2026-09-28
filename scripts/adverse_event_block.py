#!/usr/bin/env python3
"""Adverse-event purchase block: does pausing new buys after bad news help?

Tests one candidate addition to the hard risk rules (PROCESS.md §4): after a
company-specific adverse event (production cut, cost increase, outage, funding
problem), block NEW purchases of that name for N trading sessions (default 5).

Reads (never writes):
  research/pls_adverse_events/events.json          deduplicated events; each has
                                                   the UTC timestamp of the FIRST
                                                   story that reported it
  research/pls_adverse_events/prices_pls_asx.json  IBKR daily ASX sessions
                                                   (Australia/Sydney dates) plus
                                                   dividends (for total return)
  research/pls_adverse_events/prices_xjo.json      S&P/ASX 200, same calendar
Writes:
  research/pls_adverse_events/results.json         every number in the report
  reports/pls_adverse_event_block.md               the write-up tables + verdict

Timing: an event is "actionable" in the first session whose close comes after
the first report. A story timestamped before 16:00 Sydney on a trading day is
actionable that day (a buy at that day's close is post-news); anything later,
or on a non-trading day, is actionable the next session. The block covers that
reaction session and the next N-1 sessions (N in total).

Decision criteria were fixed BEFORE the first run (see PASS_RULES) so the
verdict is not fitted to the results. Stdlib only.

Usage:
    python3 scripts/adverse_event_block.py [--block 5] [--seed 7] [--placebo 2000]
                                           [--events PATH] [--no-write]
"""
from __future__ import annotations

import argparse
import bisect
import datetime as dt
import json
import math
import pathlib
import random
import statistics as st
from zoneinfo import ZoneInfo

ROOT = pathlib.Path(__file__).resolve().parent.parent
RES = ROOT / "research" / "pls_adverse_events"
REPORT = ROOT / "reports" / "pls_adverse_event_block.md"
SYD = ZoneInfo("Australia/Sydney")
ASX_CLOSE = dt.time(16, 0)
STUDY_END = dt.date(2026, 9, 23)        # last decision date (news cut-off)
HORIZONS = (5, 20, 60)                  # forward sessions for entry quality
SENS_BLOCKS = (3, 5, 10)                # block-length sensitivity

# Pre-registered pass rules (fixed before looking at results).
PASS_RULES = [
    "1. Every-session test: blocked sessions' mean 20-session forward return, "
    "market-adjusted, is below allowed sessions' and the placebo p-value is <= 0.10.",
    "2. Post-event drift from the reaction-session close to the close five sessions "
    "later is negative on average AND in the median.",
    "3. The block (blocked signals skipped, not deferred) improves at least 2 of the 3 "
    "rule-based strategies: dip-buy mean trade return, trend mean trade return, weekly "
    "DCA average cost (DCA defers the blocked buy to the first allowed session).",
]


# ── data ─────────────────────────────────────────────────────────────────────
def load_prices():
    pls = json.loads((RES / "prices_pls_asx.json").read_text())
    xjo = json.loads((RES / "prices_xjo.json").read_text())
    xmap = {r["date"]: r["close"] for r in xjo["sessions"]}
    divs = {d["exDate"]: d["amount"] for d in pls.get("dividends", [])}
    dates, close, tr, mkt = [], [], [], []
    for r in pls["sessions"]:
        if r["date"] not in xmap:
            continue
        c = float(r["close"])
        if tr:
            tr.append(tr[-1] * (c + divs.get(r["date"], 0.0)) / close[-1])
        else:
            tr.append(1.0)
        dates.append(dt.date.fromisoformat(r["date"]))
        close.append(c)
        mkt.append(float(xmap[r["date"]]))
    return dates, close, tr, mkt


def load_events(path: pathlib.Path):
    doc = json.loads(path.read_text())
    return doc, doc["events"]


def parse_utc(ts: str) -> dt.datetime:
    t = dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))
    return t if t.tzinfo else t.replace(tzinfo=dt.timezone.utc)


def reaction_index(ts_utc: str, dates: list[dt.date]) -> int | None:
    """Index of the first session whose close is after the first report."""
    local = parse_utc(ts_utc).astimezone(SYD)
    d = local.date()
    i = bisect.bisect_left(dates, d)
    if i < len(dates) and dates[i] == d and local.time() < ASX_CLOSE:
        return i
    j = bisect.bisect_right(dates, d)
    return j if j < len(dates) else None


# ── helpers ──────────────────────────────────────────────────────────────────
def fwd(series, i, h):
    return series[i + h] / series[i] - 1 if i + h < len(series) else None


def summ(xs):
    xs = [x for x in xs if x is not None]
    if not xs:
        return {"n": 0}
    return {"n": len(xs), "mean": st.fmean(xs), "median": st.median(xs),
            "hit": sum(x > 0 for x in xs) / len(xs)}


def blocked_set(react_idx, n, last):
    s = set()
    for r in react_idx:
        s.update(range(r, min(r + n, last + 1)))
    return s


def sma(xs, n, i):
    return sum(xs[i - n + 1:i + 1]) / n if i >= n - 1 else None


def sd(xs, n, i):
    return st.pstdev(xs[i - n + 1:i + 1]) if i >= n - 1 else None


# ── tests ────────────────────────────────────────────────────────────────────
def every_session(tr, mkt, decision_idx, blocked, h):
    """Split all candidate buy sessions into blocked vs allowed."""
    out = {}
    for label, adj in (("raw", False), ("mktAdj", True)):
        b, a = [], []
        for i in decision_idx:
            r = fwd(tr, i, h)
            if r is None:
                continue
            if adj:
                r -= fwd(mkt, i, h)
            (b if i in blocked else a).append(r)
        out[label] = {"blocked": summ(b), "allowed": summ(a),
                      "diff": (st.fmean(b) - st.fmean(a)) if b and a else None}
    return out


def placebo(tr, mkt, decision_idx, n_events, n_block, h, obs_diff, reps, seed):
    """Random event dates, same count: how often is the gap at least as bad?"""
    rng = random.Random(seed)
    pool = decision_idx[:-h] if h < len(decision_idx) else decision_idx
    last = decision_idx[-1]
    worse, diffs = 0, []
    for _ in range(reps):
        fake = rng.sample(pool, n_events)
        blk = blocked_set(fake, n_block, last)
        res = every_session(tr, mkt, decision_idx, blk, h)["mktAdj"]["diff"]
        if res is None:
            continue
        diffs.append(res)
        worse += res <= obs_diff
    return {"reps": len(diffs), "p": worse / len(diffs) if diffs else None,
            "placeboMeanDiff": st.fmean(diffs) if diffs else None}


def run_trades(entries_fn, exit_fn, n_sess, tr):
    """Generic one-position-at-a-time backtest; returns list of (entry, exit, ret)."""
    trades, i = [], 0
    while i < n_sess:
        e = entries_fn(i)
        if e is None:
            i += 1
            continue
        x = exit_fn(e)
        if x is None or x >= n_sess:
            break
        trades.append((e, x, tr[x] / tr[e] - 1))
        i = x + 1
    return trades


def strat_stats(trades):
    rets = [t[2] for t in trades]
    if not rets:
        return {"trades": 0}
    comp = math.prod(1 + r for r in rets) - 1
    return {"trades": len(rets), "meanTrade": st.fmean(rets), "medianTrade": st.median(rets),
            "hit": sum(r > 0 for r in rets) / len(rets), "compounded": comp}


def dip_buy(close, tr, last, blocked, mode):
    """Buy when close < SMA20 - 2 sd (Bollinger lower band); hold 20 sessions."""
    def signal(i):
        m, s = sma(close, 20, i), sd(close, 20, i)
        return m is not None and close[i] < m - 2 * s

    def entry(i):
        if i > last or not signal(i):
            return None
        if i not in blocked:
            return i
        if mode == "skip":
            return None
        j = i
        while j in blocked and j <= last:
            j += 1
        return j if j <= last else None

    return run_trades(entry, lambda e: e + 20, len(tr), tr)


def trend(close, tr, last, blocked, mode):
    """Enter when close crosses above SMA50; exit when it closes back below."""
    def cross(i):
        a, b = sma(close, 50, i - 1), sma(close, 50, i)
        return a is not None and close[i - 1] <= a and close[i] > b

    def above(i):
        m = sma(close, 50, i)
        return m is not None and close[i] > m

    def entry(i):
        if i > last or i < 51 or not cross(i):
            return None
        if i not in blocked:
            return i
        if mode == "skip":
            return None
        j = i
        while j in blocked and j <= last:
            j += 1
        return j if j <= last and above(j) else None

    def exit_(e):
        k = e + 1
        while k < len(close) and above(k):
            k += 1
        return k if k < len(close) else None

    return run_trades(entry, exit_, len(tr), tr)


def dca(dates, tr, last, blocked):
    """Invest 1 unit at the first session of each ISO week; blocked → defer."""
    buys_base, buys_blk, seen = [], [], set()
    for i in range(last + 1):
        wk = dates[i].isocalendar()[:2]
        if wk in seen:
            continue
        seen.add(wk)
        buys_base.append(i)
        j = i
        while j in blocked and j <= last:
            j += 1
        buys_blk.append(j if j <= last else last)
    units_base = sum(1 / tr[i] for i in buys_base)
    units_blk = sum(1 / tr[i] for i in buys_blk)
    deferred = sum(a != b for a, b in zip(buys_base, buys_blk))
    return {"buys": len(buys_base), "deferred": deferred,
            "avgCostImprovementBps": (units_blk / units_base - 1) * 1e4}


def event_rows(events, react, dates, tr, mkt):
    rows = []
    for ev, r in zip(events, react):
        if r is None or r == 0:
            continue
        row = {"event_id": ev["event_id"], "category": ev["category"],
               "severity": ev.get("severity"), "firstReportUtc": ev["first_report_utc"],
               "reactionSession": dates[r].isoformat(),
               "reactionDay": tr[r] / tr[r - 1] - 1,
               "reactionDayMktAdj": (tr[r] / tr[r - 1]) - (mkt[r] / mkt[r - 1])}
        for h in (5, 20, 60):
            f = fwd(tr, r, h)
            row[f"drift{h}"] = f
            row[f"drift{h}MktAdj"] = None if f is None else f - fwd(mkt, r, h)
        rows.append(row)
    return rows


# ── main ─────────────────────────────────────────────────────────────────────
def analyse(events, dates, close, tr, mkt, n_block, reps, seed):
    last = max(i for i, d in enumerate(dates) if d <= STUDY_END)
    decision_idx = list(range(50, last + 1))   # allow 50 sessions of indicator warm-up
    react = [reaction_index(e["first_report_utc"], dates)
             if e.get("first_report_utc") else None for e in events]
    in_window = [r for r in react if r is not None and r <= last]
    blocked = blocked_set(in_window, n_block, last)
    blocked_dec = blocked & set(decision_idx)
    res = {"blockSessions": n_block, "eventsTested": len(in_window),
           "sessionsInStudy": len(decision_idx), "sessionsBlocked": len(blocked_dec),
           "everySession": {}, "placebo": {}}
    for h in HORIZONS:
        es = every_session(tr, mkt, decision_idx, blocked, h)
        res["everySession"][h] = es
        if h == 20 and es["mktAdj"]["diff"] is not None:
            res["placebo"][h] = placebo(tr, mkt, decision_idx, len(in_window), n_block, h,
                                        es["mktAdj"]["diff"], reps, seed)
    rows = event_rows(events, react, dates, tr, mkt)
    rows = [r for r in rows if dt.date.fromisoformat(r["reactionSession"]) <= STUDY_END]
    res["drift"] = {k: summ([r[k] for r in rows])
                    for k in ("reactionDay", "reactionDayMktAdj", "drift5", "drift5MktAdj",
                              "drift20", "drift20MktAdj", "drift60", "drift60MktAdj")}
    strat = {}
    for name, fn in (("dipBuy", dip_buy), ("trend", trend)):
        base = strat_stats(fn(close, tr, last, set(), "skip"))
        strat[name] = {"base": base,
                       "skip": strat_stats(fn(close, tr, last, blocked, "skip")),
                       "defer": strat_stats(fn(close, tr, last, blocked, "defer"))}
    strat["dca"] = dca(dates, tr, last, blocked)
    res["strategies"] = strat
    return res, rows, react


def verdict(main):
    es20 = main["everySession"][20]["mktAdj"]
    p = (main["placebo"].get(20) or {}).get("p")
    c1 = es20["diff"] is not None and es20["diff"] < 0 and p is not None and p <= 0.10
    d5 = main["drift"]["drift5"]
    c2 = d5.get("n", 0) > 0 and d5["mean"] < 0 and d5["median"] < 0
    s = main["strategies"]

    def better(k):
        b, v = s[k]["base"], s[k]["skip"]
        return v.get("trades", 0) > 0 and b.get("trades", 0) > 0 and v["meanTrade"] > b["meanTrade"]

    wins = sum([better("dipBuy"), better("trend"), s["dca"]["avgCostImprovementBps"] > 0])
    c3 = wins >= 2
    return {"rule1": c1, "rule2": c2, "rule3": c3, "strategyWins": wins,
            "passed": c1 and c2 and c3}


def pct(x, d=1):
    return "n/a" if x is None else f"{x * 100:+.{d}f}%"


def share(s):
    return "n/a" if not s.get("n") else f"{s['hit']:.0%}"


def pval(m, h=20):
    p = (m["placebo"].get(h) or {}).get("p")
    return "n/a" if p is None else f"{p:.3f}"


def write_report(meta, main, sens, subsets, rows, v, n_block):
    L = []
    L.append("# PLS adverse-event purchase block: test results\n")
    L.append(f"_Generated by `scripts/adverse_event_block.py` on {dt.date.today().isoformat()}. "
             "Do not hand-edit; rerun the script._\n")
    L.append("## The rule tested\n")
    L.append(f"After a PLS-specific adverse event (production cut, cost increase, outage, "
             f"funding problem), block new purchases for **{n_block} trading sessions**, counting "
             "the first session whose close is after the first report.\n")
    L.append("## Data\n")
    L.append(f"- Events: {meta.get('source', 'Bigdata.com')}. News window {meta.get('newsWindow')}. "
             f"{meta.get('nStories', '?')} stories, deduplicated to {meta.get('nEvents', '?')} events.")
    L.append("- Prices: IBKR daily ASX bars 30 Sep 2021 to 28 Sep 2026, total return "
             "(3 dividends added back). Market benchmark: S&P/ASX 200 (XJO).")
    L.append(f"- Events tested against prices: {main['eventsTested']}. Events before "
             "30 Sep 2021 are catalogued but untested (no daily price source reachable).")
    L.append(f"- Candidate buy sessions: {main['sessionsInStudy']}; blocked by the rule: "
             f"{main['sessionsBlocked']} ({main['sessionsBlocked'] / main['sessionsInStudy']:.0%}).\n")
    L.append("## Pre-registered pass rules\n")
    L += PASS_RULES
    L.append("")
    L.append(f"## Verdict: **{'PASS' if v['passed'] else 'NOT SUPPORTED'}**\n")
    L.append(f"| Rule | Result |\n|---|---|\n| 1. Every-session, placebo-tested | "
             f"{'pass' if v['rule1'] else 'fail'} |\n| 2. Post-event 5-session drift negative | "
             f"{'pass' if v['rule2'] else 'fail'} |\n| 3. Improves ≥2 of 3 strategies | "
             f"{'pass' if v['rule3'] else 'fail'} ({v['strategyWins']}/3) |\n")
    L.append("## 1. Every session as a candidate buy\n")
    L.append("| Horizon | Blocked mean | Allowed mean | Gap | Blocked (mkt-adj) | Allowed (mkt-adj) | Gap (mkt-adj) |")
    L.append("|---|---|---|---|---|---|---|")
    for h, es in main["everySession"].items():
        r, m = es["raw"], es["mktAdj"]
        L.append(f"| {h} sessions | {pct(r['blocked'].get('mean'))} | {pct(r['allowed'].get('mean'))} | "
                 f"{pct(r['diff'])} | {pct(m['blocked'].get('mean'))} | {pct(m['allowed'].get('mean'))} | "
                 f"{pct(m['diff'])} |")
    pl = main["placebo"].get(20, {})
    L.append(f"\nPlacebo (20-session, market-adjusted gap): {pl.get('reps')} random draws of the same "
             f"number of event dates. Share of draws with a gap at least as negative: "
             f"**p = {pval(main)}** "
             f"(placebo mean gap {pct(pl.get('placeboMeanDiff'))}).\n")
    L.append("## 2. What the stock does after an event\n")
    L.append("| Window | n | Mean | Median | Share positive |\n|---|---|---|---|---|")
    labels = {"reactionDay": "Reaction day (close before → reaction close)",
              "reactionDayMktAdj": "Reaction day, mkt-adj",
              "drift5": "Reaction close → +5 sessions", "drift5MktAdj": "  … mkt-adj",
              "drift20": "Reaction close → +20 sessions", "drift20MktAdj": "  … mkt-adj",
              "drift60": "Reaction close → +60 sessions", "drift60MktAdj": "  … mkt-adj"}
    for k, lab in labels.items():
        s = main["drift"][k]
        L.append(f"| {lab} | {s.get('n', 0)} | {pct(s.get('mean'))} | {pct(s.get('median'))} | "
                 f"{share(s)} |")
    L.append("\n## 3. Rule-based strategies with and without the block\n")
    L.append("| Strategy | Variant | Trades | Mean trade | Median trade | Hit rate | Compounded |")
    L.append("|---|---|---|---|---|---|---|")
    for name, lab in (("dipBuy", "Dip-buy (Bollinger 20/2, hold 20)"), ("trend", "Trend (SMA50 cross)")):
        for var in ("base", "skip", "defer"):
            s = main["strategies"][name][var]
            if not s.get("trades"):
                L.append(f"| {lab} | {var} | 0 | | | | |")
                continue
            L.append(f"| {lab} | {var} | {s['trades']} | {pct(s['meanTrade'])} | {pct(s['medianTrade'])} | "
                     f"{s['hit']:.0%} | {pct(s['compounded'])} |")
    d = main["strategies"]["dca"]
    L.append(f"\nWeekly DCA: {d['buys']} weekly buys, {d['deferred']} deferred by the block. "
             f"Average-cost improvement from deferring: **{d['avgCostImprovementBps']:+.1f} bps** "
             "(positive = the block bought cheaper).\n")
    L.append("## 4. Sensitivity\n")
    L.append("| Variant | Events | Blocked sessions | 20d gap (mkt-adj) | Placebo p | 5-session drift mean / median | Strategy wins |")
    L.append("|---|---|---|---|---|---|---|")
    for lab, (m, vv) in list(sens.items()) + list(subsets.items()):
        d5 = m["drift"]["drift5"]
        L.append(f"| {lab} | {m['eventsTested']} | {m['sessionsBlocked']} | "
                 f"{pct(m['everySession'][20]['mktAdj']['diff'])} | {pval(m)} | "
                 f"{pct(d5.get('mean'))} / {pct(d5.get('median'))} | {vv['strategyWins']}/3 |")
    L.append("\n## 5. Event-by-event\n")
    L.append("| Event | Category | Sev | First report (UTC) | Reaction session | Reaction day | +5 | +20 | +20 mkt-adj |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        L.append(f"| {r['event_id']} | {r['category']} | {r.get('severity')} | {r['firstReportUtc']} | "
                 f"{r['reactionSession']} | {pct(r['reactionDay'])} | {pct(r['drift5'])} | "
                 f"{pct(r['drift20'])} | {pct(r['drift20MktAdj'])} |")
    L.append("\n## Caveats\n")
    L.append("- One stock, about five years, a few dozen events: low statistical power. Treat p-values as indicative.")
    L.append("- Forward windows overlap, so session-level observations are autocorrelated; the placebo keeps the "
             "same series and block structure to account for that.")
    L.append("- The event list depends on what Bigdata.com indexed and on the classification; first-report "
             "timestamps can lag the actual ASX release by minutes to hours.")
    L.append("- Market adjustment uses the ASX 200, not a lithium benchmark, so sector-wide lithium moves remain in the numbers.")
    REPORT.write_text("\n".join(L) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--block", type=int, default=5)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--placebo", type=int, default=2000)
    ap.add_argument("--events", type=pathlib.Path, default=RES / "events.json",
                    help="events file (default research/pls_adverse_events/events.json)")
    ap.add_argument("--no-write", action="store_true",
                    help="print the verdict only; do not write results.json or the report")
    a = ap.parse_args()

    dates, close, tr, mkt = load_prices()
    meta, events = load_events(a.events)
    main_res, rows, _ = analyse(events, dates, close, tr, mkt, a.block, a.placebo, a.seed)
    v = verdict(main_res)

    sens = {}
    for n in SENS_BLOCKS:
        if n == a.block:
            continue
        m, _, _ = analyse(events, dates, close, tr, mkt, n, a.placebo, a.seed)
        sens[f"Block {n} sessions"] = (m, verdict(m))
    subsets = {}
    for lab, keep in (("Severity ≥ 2 only", lambda e: (e.get("severity") or 0) >= 2),
                      ("Company disclosures first", lambda e: e.get("first_is_company_disclosure")),
                      ("production_cut only", lambda e: e["category"] == "production_cut"),
                      ("cost_increase only", lambda e: e["category"] == "cost_increase"),
                      ("outage only", lambda e: e["category"] == "outage"),
                      ("funding_problem only", lambda e: e["category"] == "funding_problem")):
        sub = [e for e in events if keep(e)]
        if len(sub) < 3:
            continue
        m, _, _ = analyse(sub, dates, close, tr, mkt, a.block, a.placebo, a.seed)
        subsets[lab] = (m, verdict(m))

    out = {"generatedAt": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
           "passRules": PASS_RULES, "verdict": v, "main": main_res,
           "sensitivity": {k: {"result": m, "verdict": vv} for k, (m, vv) in sens.items()},
           "subsets": {k: {"result": m, "verdict": vv} for k, (m, vv) in subsets.items()},
           "events": rows}
    if not a.no_write:
        (RES / "results.json").write_text(json.dumps(out, indent=2, default=str))
        write_report(meta, main_res, sens, subsets, rows, v, a.block)
    print(f"verdict: {'PASS' if v['passed'] else 'NOT SUPPORTED'} "
          f"(rule1={v['rule1']} rule2={v['rule2']} rule3={v['rule3']}); "
          f"events tested {main_res['eventsTested']}, sessions blocked "
          f"{main_res['sessionsBlocked']}/{main_res['sessionsInStudy']}")
    if not a.no_write:
        print(f"wrote {REPORT.relative_to(ROOT)} and {(RES / 'results.json').relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
