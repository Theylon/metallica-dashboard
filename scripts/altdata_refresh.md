# Runbook — Alt-Data tab refresh (M Science method)

A fresh Claude session (scheduled Routine, fired on trading days) follows this to refresh
the **Alt-Data tab** — a pre-earnings KPI **nowcast vs. consensus**, a **track record**,
**driver drill-down** and an analyst **narrative**, for the metals **book** and a
consumer/TMT **watchlist**. It writes research shards to `data/altdata_src/`, rebuilds
`data/altdata.json`, and commits to `master` (data-only, like the other refreshes).

**What we port is the *method*, not anyone's report.** All numbers come from our own live
MCP/web feeds. Do **not** copy proprietary third-party report text/figures (e.g. M Science,
Maiden Century, YipitData) into the repo — those are licensed to the user personally.

## 0. Prereqs
- Work on `master` (`git fetch origin master && git checkout master && git pull`). Data-only.
- Coverage is self-describing: `data/altdata_src/watchlist.json` lists the consumer/TMT
  watchlist + per-name KPI mapping and the metal→driver map; the book group is derived at
  build time from `data/positions.json`. A plain `python3 scripts/altdata_build.py` always
  yields a valid `altdata.json`, so every MCP step below is best-effort.

## 1. Book (metals) — driver mosaic
For each held metal group (from positions.json categories: Aluminum, Lithium, Steel, Precious…):
- `mcp__metalminer__ask` — one metal per question ("What is the current <metal> price and the
  industrial buying strategy for <metal>?"). Use canonical names (e.g. "lithium carbonate",
  "steel HRC", "primary aluminum LME"); descriptive qualifiers trigger wrong fuzzy matches.
- Optionally `mcp__Bigdata_com__bigdata_sentiment_tearsheet` (resolve `rp_entity_id` once via
  `find_securities`) and a `WebSearch` for demand/inventory/premium context (LME/SHFE stocks,
  China PMI/property, EV/battery demand).
Set each book name's `signal` (bullish/bearish/neutral vs. the held side), `narrative`, and
`drivers[]` ({dim, label, note}). Book names usually have no consensus KPI — leave `kpi` null
unless a name (e.g. TSLA) has a clean FMP consensus.

## 2. Watchlist (consumer / TMT) — the real nowcast
For each watchlist name (NKE, AFRM, CMG, LYFT, UBER, DASH, ABNB, ONON, DECK, CROX, BIRK, SBUX…):
- **Alt-data read (CarbonArc):** `mcp__CarbonArcMCP__search_insights` first (free) to find the
  right metric/panel, then `mcp__CarbonArcMCP__text_to_insight` (billable — scope tightly) for
  the KPI proxy, e.g. "Show <Company> monthly US credit card spend over the last 18 months".
  Populate `trend` ({label, unit, points:[{date,v}]}) and summarize momentum in `narrative`.
  NB: raw panel spend is **not** panel-size-normalized — read Y/Y with care (prefer the
  Constant-Shopper panel, or short-window momentum) and don't publish a distorted Y/Y.
- **Consensus + reported (FMP):** `mcp__FMP__calendar` endpoint `earnings-company` gives
  `revenueEstimated` (consensus) + `revenueActual` per quarter and the next earnings date —
  this drives `kpi.consensus`, `kpi.earningsDate`, and the `trackRecord[]` (est/cons vs
  reported, `deltaToReported`). NB: the FMP **Free** plan gates `analyst`/most `calendar`
  endpoints and even `earnings-company` for some symbols — fall back to `mcp__TipRanks__ask`
  or a `WebSearch` for consensus, and leave `kpi.consensus` null where unavailable (the card
  degrades to feed-only, which is fine).
- **Our estimate (Phase 2):** once a name has ≥2 quarters of paired card-spend↔reported data,
  fit a simple calibration (card-spend growth → KPI growth) and set `kpi.ourEst` + `deltaPct`
  vs consensus. Until calibrated, leave `ourEst` null (UI shows "—").
- Sentiment/theses: `mcp__Bigdata_com__bigdata_search` for a broker/news read to sharpen the
  `narrative` — paraphrase, cite the source in `sources[]`, never paste licensed report text.

## 3. Write shards + rebuild
Write normalized items into `data/altdata_src/alt_r0.json` … `alt_rN.json` (same shape as the
seed `alt_r0.json`; the builder overlays them onto auto-generated defaults by ticker; higher
shard numbers win). If the universe is too heavy for one run, refresh a rotating slice/day —
the rest keeps yesterday's shard.
```
python3 scripts/altdata_build.py     # writes data/altdata.json
```
Sanity: `counts.book` == held-name count, `counts.watchlist` == watchlist length,
`counts.researched` ≥ your refreshed slice. Eyeball a couple of cards and the nowcast rows.
First run: confirm the FMP/CarbonArc field paths match real output and adjust the seed shard
shape if a tool's response differs.

## 4. Commit to master
```
git add data/altdata.json data/altdata_src/
git commit -m "Alt-Data refresh: nowcast, drivers, track record"
git push origin master
```
GitHub Pages redeploys on push. Do **not** open a PR — scheduled data-only refresh to master,
same as the hourly price commits.

## Notes
- Nothing is executed on the account — analysis only.
- If MCP servers are unavailable in the fired session, just rebuild from the committed
  `data/altdata_src/` and commit — the tab stays valid and the next successful run refreshes it.
- Scheduling: wire this as a Claude Routine (CronCreate) the same way the Stock-Picks research
  routine (`scripts/micro_refresh_research.md`) is scheduled.
