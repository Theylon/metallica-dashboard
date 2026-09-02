#!/usr/bin/env python3
"""Does a MetalMiner rare-earth assessment lead, confirm, or contradict the rare-earth equities?

Reads a MetalMiner historical dump (licensed — path on the command line, never
committed) and an equities file `{ticker: {"YYYY-MM-DD": close}}` assembled by the
caller from IBKR / TrueNorth (also never committed), and writes
reports/rare_earth_leadlag.md with three tests per ticker plus pooled:

  1. weekly cross-correlation of log changes, commodity lead k = -4..+4 weeks
     (k > 0: the commodity moved first; k < 0: the stock moved first)
  2. trend test: sign/size of the commodity's trailing LOOK-day change (published
     DELAY trading days late) vs the stock's forward FWD-day return — Spearman IC,
     block-bootstrap p, first/second-half split, and a long-when-up rule vs buy & hold
  3. divergence test: the 3x3 grid of (stock trailing LOOK-day move) x (commodity
     trailing LOOK-day move) at +-THRESH sd, forward FWD-day stock return per cell,
     the episode list for the "stock up / commodity down" cell, and a block-bootstrap
     p for that cell against random contiguous windows

Verdict rule (fixed in advance, no threshold search): the divergence cell counts as
CONFIRMED on a ticker when mean forward return < 0, at least MIN_EPISODES distinct
episodes, and bootstrap p < P_CONFIRM.

    python3 scripts/rare_earth_leadlag.py dump.json.gz --equities eq.json \\
        --tickers MP,REMX,LYSCF --commodity 270930 --delay 11

Defaults: commodity 270930 (PrNd oxide, China exw), DELAY 11 trading days (the gap
between a series' last observation and the dump date, i.e. what a dump user actually
sees), LOOK 20, FWD 20, THRESH 0.5 sd. MP is cut at 2020-11-18 (SPAC shell before).
Stdlib only.
"""
import argparse
import json
import math
import pathlib
import random
import statistics
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from mmi_proxy_audit import load_dump  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
REPORT = ROOT / "reports" / "rare_earth_leadlag.md"

LISTING_CUTOFF = {"MP": "2020-11-18"}  # MP Materials; the SPAC (FVAC) traded flat before
MIN_EPISODES = 6
P_CONFIRM = 0.10
BOOT = 2000
SEED = 7


# ---------- small numeric helpers (stdlib) ----------
def ffill_on(dates, series):
    """Value of `series` (date->value) as of each date in `dates`, forward-filled."""
    out, last, ks, i = [], None, sorted(series), 0
    for d in dates:
        while i < len(ks) and ks[i] <= d:
            last = series[ks[i]]
            i += 1
        out.append(last)
    return out


def logret(x):
    return [None if a in (None, 0) or b in (None, 0) else math.log(b / a) for a, b in zip(x, x[1:])]


def pearson(a, b):
    p = [(x, y) for x, y in zip(a, b) if x is not None and y is not None]
    if len(p) < 10:
        return float("nan"), len(p)
    xs, ys = [q[0] for q in p], [q[1] for q in p]
    mx, my = statistics.mean(xs), statistics.mean(ys)
    sxy = sum((x - mx) * (y - my) for x, y in p)
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    return (sxy / math.sqrt(sxx * syy) if sxx and syy else float("nan")), len(p)


def rank(v):
    order = sorted(range(len(v)), key=lambda i: v[i])
    r = [0] * len(v)
    for pos, i in enumerate(order):
        r[i] = pos
    return r


def spearman(a, b):
    return pearson(rank(a), rank(b))[0]


def mean(v):
    return statistics.mean(v) if v else float("nan")


def tstat(v):
    if len(v) < 3 or not statistics.pstdev(v):
        return float("nan")
    return statistics.mean(v) / (statistics.pstdev(v) / math.sqrt(len(v)))


def block_perm_p(sig, fr, rng, block=6):
    """Two-sided p for Spearman IC under block permutation of the signal."""
    obs = spearman(sig, fr)
    n, cnt = len(sig), 0
    for _ in range(BOOT):
        start = rng.randrange(n)
        rolled = [sig[(start + i) % n] for i in range(n)]
        idx = list(range(0, n, block))
        rng.shuffle(idx)
        perm = []
        for i in idx:
            perm += rolled[i:i + block]
        if abs(spearman(perm[:n], fr)) >= abs(obs):
            cnt += 1
    return obs, cnt / BOOT


def window_p(cell, base, rng):
    """One-sided p: mean of random contiguous windows of len(cell) from `base` <= mean(cell)."""
    if not cell or len(base) < len(cell) + 1:
        return float("nan")
    obs = mean(cell) - mean(base)
    n, cnt = len(cell), 0
    for _ in range(BOOT):
        s = rng.randrange(len(base))
        samp = [base[(s + j) % len(base)] for j in range(n)]
        if mean(samp) - mean(base) <= obs:
            cnt += 1
    return cnt / BOOT


def annualised(r, fwd):
    m = statistics.mean(r) * 252 / fwd
    sd = statistics.pstdev(r) * math.sqrt(252 / fwd)
    return m, sd, (m / sd if sd else float("nan"))


# ---------- the three tests ----------
def prepare(ticker, closes, commodity):
    cutoff = LISTING_CUTOFF.get(ticker, "0000-00-00")
    dates = sorted(d for d in closes if d >= cutoff)
    px = [closes[d] for d in dates]
    c = ffill_on(dates, commodity)
    k = next((i for i, v in enumerate(c) if v is not None), len(c))
    return dates[k:], px[k:], c[k:]


def crosscorr(px, c, kmax=4):
    rp, rc = logret(px[::5]), logret(c[::5])
    out = {}
    for k in range(-kmax, kmax + 1):
        if k >= 0:
            r, _ = pearson(rc[:len(rc) - k] if k else rc, rp[k:])
        else:
            r, _ = pearson(rc[-k:], rp[:len(rp) + k])
        out[k] = r
    return out


def trend_test(dates, px, c, look, fwd, delay, rng):
    sig, fr, when = [], [], []
    for i in range(look + delay, len(px) - fwd, fwd):
        j = i - delay
        if c[j] and c[j - look]:
            sig.append(math.log(c[j] / c[j - look]))
            fr.append(math.log(px[i + fwd] / px[i]))
            when.append(dates[i])
    if len(sig) < 12:
        return None
    ic, p = block_perm_p(sig, fr, rng)
    half = len(sig) // 2
    up = [f for s, f in zip(sig, fr) if s > 0]
    return {
        "n": len(sig), "ic": ic, "p": p,
        "ic1": spearman(sig[:half], fr[:half]), "ic2": spearman(sig[half:], fr[half:]),
        "split": when[half],
        "bh": annualised(fr, fwd),
        "long_up": annualised([f if s > 0 else 0.0 for s, f in zip(sig, fr)], fwd),
        "ls": annualised([f if s > 0 else -f for s, f in zip(sig, fr)], fwd),
        "time_in": len(up) / len(sig),
    }


def divergence_test(dates, px, c, look, fwd, delay, thresh, rng):
    idx = range(look + delay, len(px) - fwd)
    sr = {i: math.log(px[i] / px[i - look]) for i in idx}
    cr = {i: math.log(c[i - delay] / c[i - delay - look]) for i in idx if c[i - delay] and c[i - delay - look]}
    fr = {i: math.log(px[i + fwd] / px[i]) for i in idx}
    idx = [i for i in idx if i in cr]
    if len(idx) < 60:
        return None
    ss, cs = statistics.pstdev([sr[i] for i in idx]), statistics.pstdev([cr[i] for i in idx])

    def state(v, sd):
        return "up" if v > thresh * sd else "down" if v < -thresh * sd else "flat"

    cells = {}
    for i in idx[::fwd]:  # non-overlapping sampling
        cells.setdefault((state(sr[i], ss), state(cr[i], cs)), []).append(fr[i])
    # episodes of the up/down cell (gap > 30 trading days starts a new episode)
    hits = [i for i in idx if state(sr[i], ss) == "up" and state(cr[i], cs) == "down"]
    episodes, last = [], None
    for i in hits:
        if last is None or i - last > 30:
            episodes.append(i)
        last = i
    weekly_cell = [fr[i] for i in hits if i % 5 == 0]
    base = [fr[i] for i in idx if i % 5 == 0]
    return {
        "sd_stock": ss, "sd_comm": cs, "cells": cells,
        "episodes": [(dates[i], sr[i], cr[i], fr[i]) for i in episodes],
        "weekly_n": len(weekly_cell), "weekly_mean": mean(weekly_cell),
        "weekly_neg": (sum(1 for x in weekly_cell if x < 0) / len(weekly_cell)) if weekly_cell else float("nan"),
        "p": window_p(weekly_cell, base, rng), "base_mean": mean(base),
        "confirmed": bool(weekly_cell) and mean(weekly_cell) < 0 and len(episodes) >= MIN_EPISODES
        and window_p(weekly_cell, base, rng) < P_CONFIRM,
    }


# ---------- report ----------
CELL_ORDER = [("up", "up"), ("up", "flat"), ("up", "down"), ("flat", "up"), ("flat", "down"),
              ("down", "up"), ("down", "flat"), ("down", "down")]


def pct(x):
    return "n/a" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x * 100:+.1f}%"


def render(results, pooled, args, comm_label, dump_name):
    L = [f"# Rare-earth lead/lag: {comm_label} vs equities", "",
         f"Dump `{dump_name}` · commodity id {args.commodity} · look {args.look}d · fwd {args.fwd}d · "
         f"publication delay {args.delay} trading days · divergence threshold ±{args.threshold_sd} sd · "
         f"tickers {', '.join(results)}.", "",
         f"Verdict rule (fixed before running): the 'stock up / commodity down' cell is CONFIRMED on a "
         f"ticker when mean fwd {args.fwd}d < 0, ≥{MIN_EPISODES} episodes, bootstrap p < {P_CONFIRM}.", ""]
    L += ["## Verdicts", "", "| ticker | window | episodes | mean fwd (weekly sample) | negative share | p | confirmed |",
          "|---|---|---|---|---|---|---|"]
    for t, r in results.items():
        d = r["div"]
        if d is None:
            L.append(f"| {t} | {r['start']}..{r['end']} | too short | | | | no |")
            continue
        L.append(f"| {t} | {r['start']}..{r['end']} | {len(d['episodes'])} | {pct(d['weekly_mean'])} (n={d['weekly_n']}) | "
                 f"{d['weekly_neg'] * 100:.0f}% | {d['p']:.3f} | **{'YES' if d['confirmed'] else 'no'}** |")
    L += ["", "## 1. Weekly cross-correlation (k>0: commodity moved first; k<0: stock moved first)", "",
          "| ticker | " + " | ".join(f"k={k:+d}" for k in range(-4, 5)) + " |", "|---|" + "---|" * 9]
    for t, r in results.items():
        L.append(f"| {t} | " + " | ".join(f"{r['xc'][k]:+.2f}" for k in range(-4, 5)) + " |")
    L += ["", f"## 2. Trend test: commodity trailing change (delayed) → stock fwd {args.fwd}d", "",
          "| ticker | look | n | IC | p | IC 1st half | IC 2nd half (from) | buy&hold ann/vol/Sharpe | long-when-up | long-short | time in |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for t, r in results.items():
        for look, tr in r["trend"].items():
            if tr is None:
                L.append(f"| {t} | {look} | too short | | | | | | | | |")
                continue
            f3 = lambda a: f"{a[0] * 100:+.0f}% / {a[1] * 100:.0f}% / {a[2]:.2f}"  # noqa: E731
            L.append(f"| {t} | {look} | {tr['n']} | {tr['ic']:+.2f} | {tr['p']:.2f} | {tr['ic1']:+.2f} | "
                     f"{tr['ic2']:+.2f} ({tr['split']}) | {f3(tr['bh'])} | {f3(tr['long_up'])} | {f3(tr['ls'])} | {tr['time_in']:.0%} |")
    L += ["", f"## 3. Divergence grid: stock {args.look}d move × commodity {args.look}d move → stock fwd {args.fwd}d", ""]
    hdr = "| stock / commodity | " + " | ".join(results) + " | pooled |"
    L += [hdr, "|---|" + "---|" * (len(results) + 1)]
    for cell in CELL_ORDER:
        row = [f"{cell[0]} / {cell[1]}"]
        for t, r in results.items():
            v = (r["div"] or {}).get("cells", {}).get(cell, [])
            row.append(f"{pct(mean(v))} (t {tstat(v):+.1f}, n={len(v)})" if v else "–")
        v = pooled.get(cell, [])
        row.append(f"{pct(mean(v))} (t {tstat(v):+.1f}, n={len(v)})" if v else "–")
        L.append("| " + " | ".join(row) + " |")
    L += ["", "### Episodes of 'stock up / commodity down' (first flagged day, trailing moves, fwd return)", ""]
    for t, r in results.items():
        if not r["div"]:
            continue
        L += [f"**{t}** — weekly-sample mean {pct(r['div']['weekly_mean'])}, unconditional weekly mean "
              f"{pct(r['div']['base_mean'])}, bootstrap p {r['div']['p']:.3f}", "",
              "| first day | stock trailing | commodity trailing | stock fwd |", "|---|---|---|---|"]
        for d, s, c, f in r["div"]["episodes"]:
            L.append(f"| {d} | {pct(s)} | {pct(c)} | {pct(f)} |")
        L.append("")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("dump")
    ap.add_argument("--equities", required=True, help='JSON {ticker: {"YYYY-MM-DD": close}}')
    ap.add_argument("--tickers", default="MP,REMX,LYSCF")
    ap.add_argument("--commodity", type=int, default=270930)
    ap.add_argument("--delay", type=int, default=11)
    ap.add_argument("--look", type=int, default=20)
    ap.add_argument("--fwd", type=int, default=20)
    ap.add_argument("--threshold-sd", type=float, default=0.5)
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()
    rng = random.Random(SEED)

    series, meta = load_dump(args.dump)
    if args.commodity not in series:
        raise SystemExit(f"commodity {args.commodity} not in dump")
    commodity = series[args.commodity]
    equities = json.loads(pathlib.Path(args.equities).read_text())

    results, pooled = {}, {}
    for t in [x for x in args.tickers.split(",") if x]:
        if t not in equities:
            print(f"skip {t}: not in equities file", file=sys.stderr)
            continue
        dates, px, c = prepare(t, equities[t], commodity)
        if len(dates) < 250:
            print(f"skip {t}: only {len(dates)} trading days after cutoff", file=sys.stderr)
            continue
        div = divergence_test(dates, px, c, args.look, args.fwd, args.delay, args.threshold_sd, rng)
        results[t] = {
            "start": dates[0], "end": dates[-1],
            "xc": crosscorr(px, c),
            "trend": {look: trend_test(dates, px, c, look, args.fwd, args.delay, rng) for look in (args.look, 60)},
            "div": div,
        }
        if div:
            for cell, v in div["cells"].items():
                pooled.setdefault(cell, []).extend(v)

    text = render(results, pooled, args, meta[args.commodity], pathlib.Path(args.dump).name)
    print(text)
    if not args.no_write:
        REPORT.parent.mkdir(exist_ok=True)
        REPORT.write_text(text)
        print(f"wrote {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
