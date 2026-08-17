#!/usr/bin/env python3
"""Track and report each holding's commodity exposure over the time it is held.

Forward-looking only: appends one dated snapshot per refresh to
data/position_history.jsonl (never backfilled, since no historical trade
ledger exists). Joins the accumulated history against a two-layer mapping to
produce a per-day, per-commodity weighted exposure series, written to
data/exposure_history.json and a human-readable report at
reports/asset_commodity_exposure.md.

The mapping layers (the part that must stay economically accurate):
  1. Curated primary links — every ticker that can enter the book (the
     CATEGORY roster in mcp_refresh.py) gets an explicit link to the metal it
     actually produces/tracks (CATEGORY_PRIMARY / TICKER_PRIMARY below). These
     never depend on the mined map, so a pure-play copper miner can't end up
     with zero copper exposure. The link's tier comes from the name's curated
     price sensitivity (micro.json OM linkage): producers (priceSens 3) at T1,
     partial pass-through (2) at T2, and metal-price-neutral fabricators
     (priceSens 1, e.g. KALU/CSTM) carry NO metal-price link at all — their
     real exposure is conversion margin, not the primary metal.
  2. Mined statistical links — data/linkage_map.json (signal-mined from
     rolling price correlations) supplies supplementary links, T1/T2 only,
     family-filtered (see FAMILY) so artifacts like smelter->cobalt are
     dropped, and commodity names canonicalized (see COMMODITY_CANON) so
     variants of one real-world exposure ("aluminum" vs "aluminum n", "lco"
     vs "lithium carbonate") can't double count.

Weighting: exposure(day, commodity) = sum over held tickers linked to that
commodity of (position's % of NAV) * tier_weight, where tier_weight is
T1=1.0, T2=0.5 (T3/T4 excluded entirely).

Run standalone against the current data/positions.json + data/account.json,
or import record_and_report() and call it from mcp_refresh.py after those
two files are (re)written.
"""
import json
import pathlib
import sys
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
REPORTS = ROOT / "reports"

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from mcp_refresh import CATEGORY as TICKER_CATEGORY  # noqa: E402  (needs sys.path above)

TIER_WEIGHT = {"T1": 1.0, "T2": 0.5}  # T3/T4 excluded per methodology tier cutoff

# Mined commodity-name variants -> the one real-world exposure they represent.
# The mined map quotes the same underlying commodity under several contract
# names ("aluminum" and "aluminum n", "lco"/"lmo"/"lithium carbonate" are all
# battery-lithium chemistry) — without folding them, one position counts the
# same exposure two or three times and the dashboard table shows chemistry
# jargon instead of metals. Names not listed pass through unchanged.
COMMODITY_CANON = {
    "aluminum n": "aluminum",
    "aluminum mmi": "aluminum",
    "copper mmi": "copper",
    "raw steels mmi": "steel",
    "electrical steel": "steel",
    "goes mmi": "steel",
    "201": "stainless steel",
    "stainless mmi": "stainless steel",
    "lco": "lithium",
    "lmo carbonate-based": "lithium",
    "lmo hydroxide-based": "lithium",
    "nmc111 carbonate-based": "lithium",
    "lithium carbonate": "lithium",
    "lithium hydroxide monohydrate": "lithium",
    "cobalt sulfate": "cobalt",
    "manganese dioxide": "manganese",
    "manganese sulfate": "manganese",
    "molybdenum bar": "molybdenum",
    "titanium plate": "titanium",
    "titanium sponge": "titanium",
    "rare earths mmi": "rare earths",
    "global precious metals mmi": "precious metals",
}

# equity_group -> commodity substrings that are economically plausible exposure.
# The linkage map is signal-mined from rolling price correlations, so it carries
# statistical artifacts (e.g. an aluminum smelter "linked" T1 to cobalt sulfate).
# Its own validation gates reject nearly every link (364/375 sampled fail
# passes_all_gates), so gating alone would keep almost nothing — this allowlist
# is the sanity layer instead: a link only counts when the commodity belongs to
# the equity group's actual product family. Matched against canonicalized
# commodity names (see COMMODITY_CANON). Groups not listed pass through
# unfiltered (new groups should be added here as the map grows).
FAMILY = {
    "Aluminum Equity": ("aluminum",),
    "Battery Equity": ("lithium", "cobalt", "manganese", "nickel"),
    "Battery Etf": ("lithium", "cobalt", "manganese", "nickel"),
    "Copper Equity": ("copper", "molybdenum"),
    "Copper Etf": ("copper",),
    "Copper Futures": ("copper",),
    "Diversified Mining": ("iron", "copper", "aluminum", "nickel", "steel"),
    "Ev Equity": ("lithium", "cobalt", "nickel", "manganese"),
    "Gold Etf": ("gold",),
    "Gold Futures": ("gold",),
    "Lithium Miner": ("lithium",),
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


# ── Curated primary exposure ──────────────────────────────────────────────
# The mined map only knows what happened to correlate: before this layer the
# live book mapped FCX to molybdenum-but-not-copper, ALB to manganese-but-not-
# lithium, and left SCCO/HBM/TECK/CENX and the whole steel complex with no
# commodity at all. Primary product exposure is a fact about the company, not
# a statistic — so it is declared here, per dashboard category (the CATEGORY
# roster in mcp_refresh.py already names every ticker that can enter the book)
# with per-ticker overrides where a category is too coarse.
CATEGORY_PRIMARY = {
    "Lithium": ("lithium",),
    "Copper": ("copper",),
    "Steel": ("steel",),
    "Aluminum": ("aluminum",),
    "Rare Earth": ("rare earths",),
    "Uranium": ("uranium",),
    "Diversified": ("iron ore",),   # BHP/RIO/VALE: iron ore is the earnings driver
    "Mining ETF": ("steel",),       # XME is steel-dominant; rest covered below
    "Precious": (),                 # one metal per name — see TICKER_PRIMARY
    "Renewables": (),               # BEPC: no direct metal book
}

# Ticker-level primary override (categories too coarse for these).
TICKER_PRIMARY = {
    "GLD": ("gold",), "BVN": ("gold",),
    "SLV": ("silver",), "AG": ("silver",), "CDE": ("silver",),
    "HL": ("silver",), "PAAS": ("silver",),
    "PALL": ("palladium",),
    "SBSW": ("platinum", "palladium"), "PLG": ("platinum", "palladium"),
}

# Real secondary product lines (meaningful revenue, not the main driver) — T2.
TICKER_SECONDARY = {
    "FCX": ("molybdenum", "gold"),
    "SCCO": ("molybdenum",),
    "HBM": ("gold", "zinc"),
    "TECK": ("zinc",),
    "BHP": ("copper",),
    "RIO": ("aluminum", "copper"),
    "VALE": ("copper", "nickel"),
    "XME": ("gold", "copper", "aluminum"),
    "PAAS": ("gold",),
    "BVN": ("silver",),
    "UUUU": ("rare earths",),
}

# Fallback for names with no curated priceSens (see _price_sensitivity):
# downstream fabricators / demand-side proxies whose metal link is real but
# diluted by conversion margin — their primary enters at T2 (0.5) not T1.
DOWNSTREAM = {"MLI", "KALU", "WOR", "ROCK", "TSLA", "KARS"}

# priceSens (1-3, from the OM linkage research in micro.json) -> primary-link
# tier. The Aug-2026 aluminum divergence made the stakes concrete: LME primary
# rallied ~5%/month while US semi-fab sheet fell ~4% — smelters (AA/CENX,
# priceSens 3) and the fabricator (KALU, priceSens 1, "passes LME to
# customers") moved on OPPOSITE legs of that spread. A pass-through
# fabricator's real exposure is its conversion margin, which the primary
# metal price does not proxy — so priceSens 1 gets NO primary-metal link.
PRICE_SENS_TIER = {3: "T1", 2: "T2", 1: None}


def _price_sensitivity():
    """ticker -> curated priceSens (1-3) from micro.json's OM-linkage research.

    micro.json carries per-name role/priceSens with evidence (e.g. CENX
    "LME/Midwest/EDPP explicit revenue components" = 3, KALU
    "metal-price-neutral policy passes LME to customers" = 1). Missing file or
    missing per-name data degrades to {} / no entry — callers fall back to the
    static DOWNSTREAM heuristic, so the refresh never breaks on a stale micro.
    """
    try:
        rows = json.loads((DATA / "micro.json").read_text()).get("tickers", [])
    except Exception:
        return {}
    sens = {}
    for r in rows:
        ps = (r.get("exposure") or {}).get("priceSens")
        if isinstance(ps, (int, float)) and r.get("ticker"):
            sens[str(r["ticker"]).split(" @")[0].upper()] = int(ps)
    return sens


def _canon(name):
    name = str(name or "").lower()
    return COMMODITY_CANON.get(name, name)


def _family_ok(link):
    group = TICKER_GROUP_OVERRIDE.get(link.get("ticker"), link.get("equity_group"))
    fam = FAMILY.get(group)
    if fam is None:
        return True
    commodity = _canon(link.get("commodity"))
    return any(sub in commodity for sub in fam)


def curated_links():
    """Explicit primary/secondary links for every ticker in the CATEGORY roster."""
    unmapped = sorted({cat for cat in TICKER_CATEGORY.values()
                       if cat not in CATEGORY_PRIMARY})
    if unmapped:   # a new category must declare its metal (or explicitly ())
        raise ValueError(f"CATEGORY_PRIMARY missing entries for: {unmapped}")
    sens = _price_sensitivity()
    links = []
    for ticker, category in TICKER_CATEGORY.items():
        if ticker in sens:
            primary_tier = PRICE_SENS_TIER.get(sens[ticker], "T1")
        else:
            primary_tier = "T2" if ticker in DOWNSTREAM else "T1"
        if primary_tier is not None:
            for commodity in TICKER_PRIMARY.get(ticker, CATEGORY_PRIMARY[category]):
                links.append({"ticker": ticker, "commodity": commodity,
                              "tier": primary_tier, "source": "curated"})
        for commodity in TICKER_SECONDARY.get(ticker, ()):
            links.append({"ticker": ticker, "commodity": commodity,
                          "tier": "T2", "source": "curated"})
    return links


def load_linkage_map():
    """Ticker -> one entry per distinct commodity (best tier wins).

    Merges the curated primary layer (authoritative — guarantees every name in
    the CATEGORY roster maps to its real product family) with the mined map's
    supplementary links. Mined rows list a separate entry per commodity-ID
    variant (different exchange/unit contracts for the same underlying), so
    names are canonicalized and collapsed to one row per (ticker, commodity)
    to avoid counting the same real-world exposure several times over. Mined
    links outside their equity group's product family (see FAMILY) are dropped
    as statistical artifacts.
    """
    mined = json.loads((DATA / "linkage_map.json").read_text())["links"]
    passthrough = {t for t, s in _price_sensitivity().items() if s == 1}
    best = {}
    for link in mined:
        if link["tier"] not in TIER_WEIGHT:
            continue
        # Metal-price-neutral names (priceSens 1) take no metal links at all —
        # a mined correlation must not re-add what the curated layer excludes.
        if link.get("ticker") in passthrough:
            continue
        if not _family_ok(link):
            continue
        link = dict(link, commodity=_canon(link.get("commodity")))
        key = (link["ticker"], link["commodity"])
        if key not in best or TIER_WEIGHT[link["tier"]] > TIER_WEIGHT[best[key]["tier"]]:
            best[key] = link
    for link in curated_links():
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
        "Tracks each held ticker's exposure to its linked commodities — a "
        "curated primary link per name (the metal the company actually "
        "produces/tracks, from the CATEGORY roster) plus supplementary T1/T2 "
        "links mined in metallica-fund's equity_commodity_linkage.md "
        "(family-filtered, names canonicalized) — weighted by that position's "
        "% of NAV. "
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
