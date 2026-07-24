#!/usr/bin/env python3
"""Track and report each holding's commodity exposure over the time it is held.

Forward-looking only: appends one dated snapshot per refresh to
data/position_history.jsonl (never backfilled, since no historical trade
ledger exists). Joins the accumulated history against data/linkage_map.json
(T1/T2 pairs only, family-filtered — see FAMILY — so signal-mined artifacts
like smelter->cobalt links are dropped) to produce a per-day, per-commodity weighted exposure
series, written to data/exposure_history.json and a human-readable report at
reports/asset_commodity_exposure.md.

Weighting: exposure(day, commodity) = sum over held tickers linked to that
commodity of (position's % of NAV) * tier_weight, where tier_weight is
T1=1.0, T2=0.5 (T3/T4 excluded entirely).

Run standalone against the current data/positions.json + data/account.json,
or import record_and_report() and call it from mcp_refresh.py after those
two files are (re)written.
"""
import json
import pathlib
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
REPORTS = ROOT / "reports"

TIER_WEIGHT = {"T1": 1.0, "T2": 0.5}  # T3/T4 excluded per methodology tier cutoff

# equity_group -> commodity substrings that are economically plausible exposure.
# The linkage map is signal-mined from rolling price correlations, so it carries
# statistical artifacts (e.g. an aluminum smelter "linked" T1 to cobalt sulfate).
# Its own validation gates reject nearly every link (364/375 sampled fail
# passes_all_gates), so gating alone would keep almost nothing — this allowlist
# is the sanity layer instead: a link only counts when the commodity belongs to
# the equity group's actual product family. Groups not listed pass through
# unfiltered (new groups should be added here as the map grows).
FAMILY = {
    "Aluminum Equity": ("aluminum",),
    "Battery Equity": ("lithium", "lco", "lmo", "cobalt", "manganese", "nickel"),
    "Battery Etf": ("lithium", "lco", "lmo", "cobalt", "manganese", "nickel"),
    "Copper Equity": ("copper", "molybdenum"),
    "Copper Etf": ("copper",),
    "Copper Futures": ("copper",),
    "Diversified Mining": ("iron", "copper", "aluminum", "nickel", "steel"),
    "Ev Equity": ("lithium", "lco", "cobalt", "nickel", "manganese"),
    "Gold Etf": ("gold",),
    "Gold Futures": ("gold",),
    "Lithium Miner": ("lithium", "lco"),
    "Palladium Etf": ("platinum", "palladium", "rhodium", "ruthenium"),
    "Palladium Futures": ("platinum", "palladium", "rhodium", "ruthenium"),
    "Pgm Equity": ("platinum", "palladium", "rhodium", "ruthenium"),
    "Platinum Etf": ("platinum", "palladium", "rhodium", "ruthenium"),
    "Platinum Futures": ("platinum", "palladium", "rhodium", "ruthenium"),
    "Rare Earth": ("rare earth",),
    "Silver Equity": ("silver",),
    "Silver Etf": ("silver",),
    "Silver Futures": ("silver",),
    "Steel Equity": ("steel", "ferro-chrome"),
}


# Some tickers are miscategorized in the signal-mined linkage map (it clusters by
# price correlation, not fundamentals). Correct the equity_group for the family
# check so their cross-family links are dropped — e.g. MP (MP Materials, a
# rare-earth miner) is grouped "Lithium Miner" and would otherwise contribute a
# spurious lithium-carbonate (lco) exposure.
TICKER_GROUP_OVERRIDE = {"MP": "Rare Earth"}


def _family_ok(link):
    group = TICKER_GROUP_OVERRIDE.get(link.get("ticker"), link.get("equity_group"))
    fam = FAMILY.get(group)
    if fam is None:
        return True
    commodity = str(link.get("commodity", "")).lower()
    return any(sub in commodity for sub in fam)


def load_linkage_map():
    """Ticker -> one entry per distinct commodity (best tier wins).

    The source map lists a separate row per commodity-ID variant (different
    exchange/unit contracts for the same underlying commodity, e.g. aluminum
    quoted in both pounds and metric tons). Collapsing to one row per
    (ticker, commodity) avoids counting the same real-world exposure several
    times over. Links outside their equity group's product family (see FAMILY)
    are dropped as statistical artifacts.
    """
    links = json.loads((DATA / "linkage_map.json").read_text())["links"]
    best = {}
    for link in links:
        if link["tier"] not in TIER_WEIGHT:
            continue
        if not _family_ok(link):
            continue
        key = (link["ticker"], link["commodity"])
        if key not in best or TIER_WEIGHT[link["tier"]] > TIER_WEIGHT[best[key]["tier"]]:
            best[key] = link

    by_ticker = defaultdict(list)
    for (ticker, _commodity), link in best.items():
        by_ticker[ticker].append(link)
    return by_ticker


def record_snapshot(date=None):
    """Record today's held tickers + NAV weight into position_history.jsonl.

    REWRITES today's rows on every run (the refresh runs several times a day) so
    the day's snapshot converges to the end-of-day book: a name closed intraday
    drops out and a new buy appears, instead of freezing at the first-of-day book
    (which left closed names like CLF in the day's exposure and omitted new buys).
    """
    positions = json.loads((DATA / "positions.json").read_text())
    account = json.loads((DATA / "account.json").read_text())
    date = date or positions["updatedAt"][:10]
    nav = account["nav"] or 1.0

    history_path = DATA / "position_history.jsonl"
    kept = []  # every OTHER day's rows, verbatim
    if history_path.exists():
        for line in history_path.read_text().splitlines():
            if line.strip() and json.loads(line)["date"] != date:
                kept.append(line)
    today = [json.dumps({
        "date": date, "ticker": p["ticker"], "shares": p["shares"],
        "mktValue": p["mktValue"],
        "navWeight": round(p["mktValue"] / nav, 6) if nav else 0.0,
    }) for p in positions["positions"]]
    history_path.write_text("\n".join(kept + today) + "\n")


def compute_exposure_history():
    """Join position_history.jsonl against the T1/T2 linkage map."""
    by_ticker = load_linkage_map()
    history_path = DATA / "position_history.jsonl"
    if not history_path.exists():
        return {}

    by_date = defaultdict(list)
    for line in history_path.read_text().splitlines():
        if line.strip():
            row = json.loads(line)
            by_date[row["date"]].append(row)

    exposure_history = {}
    for date, rows in sorted(by_date.items()):
        commodity_exposure = defaultdict(float)
        ticker_links = defaultdict(list)
        for row in rows:
            links = by_ticker.get(row["ticker"], [])
            for link in links:
                weight = row["navWeight"] * TIER_WEIGHT[link["tier"]]
                commodity_exposure[link["commodity"]] += weight
                ticker_links[row["ticker"]].append({
                    "commodity": link["commodity"], "tier": link["tier"],
                    "weight": round(weight, 6),
                })
        exposure_history[date] = {
            "commodityExposure": {
                k: round(v, 6) for k, v in
                sorted(commodity_exposure.items(), key=lambda kv: -kv[1])
            },
            "byTicker": ticker_links,
        }
    return exposure_history


def write_report(exposure_history):
    (DATA / "exposure_history.json").write_text(
        json.dumps(exposure_history, indent=2) + "\n")

    REPORTS.mkdir(exist_ok=True)
    lines = [
        "# Asset -> Commodity Exposure Over Time",
        "",
        "Tracks each held ticker's exposure to its linked commodities (T1/T2 "
        "links from metallica-fund's equity_commodity_linkage.md, filtered to "
        "each equity group's product family) weighted by that position's % of NAV. "
        "Forward-looking only: history starts the day this tracker was turned "
        "on, there is no backfilled trade ledger.",
        "",
    ]
    for date, day in exposure_history.items():
        lines.append(f"## {date}")
        lines.append("")
        lines.append("| Commodity | Exposure (% NAV, tier-weighted) |")
        lines.append("|---|---|")
        for commodity, weight in day["commodityExposure"].items():
            lines.append(f"| {commodity} | {weight * 100:.2f}% |")
        lines.append("")
    (REPORTS / "asset_commodity_exposure.md").write_text("\n".join(lines) + "\n")


def record_and_report(date=None):
    record_snapshot(date)
    exposure_history = compute_exposure_history()
    write_report(exposure_history)
    return exposure_history


if __name__ == "__main__":
    record_and_report()
    print("Recorded snapshot and wrote data/exposure_history.json + "
          "reports/asset_commodity_exposure.md")
