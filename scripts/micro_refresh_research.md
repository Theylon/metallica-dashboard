# Runbook — daily research refresh for the Stock Picks tab (Tier 2)

A fresh Claude session (fired ~13:00 UTC on trading days by the scheduled Routine)
follows this to refresh the **research layer** of `data/micro.json` and commit it to
`master`. The **price layer** is handled separately by the GitHub Action 4×/day
(`scripts/micro_refresh.py`) — do **not** duplicate that here.

The repo is self-contained: `data/micro_src/` holds every research input, so a plain
rebuild always yields a valid `micro.json`. MCP refreshes below are best-effort — if
one fails, still rebuild and commit so the tab never goes stale or loses research.

## 0. Prereqs
- Work on `master` (data-only change, like the hourly data refresh). `git fetch origin master && git checkout master && git pull`.
- The Excel universe map lives at the path the SessionStart context references
  (`…/1835c81d-mm_materials_stock_map_enriched.xlsx`). If absent, skip
  `build_universe.py` — the committed `data/universe.json` is fine to reuse.

## 1. Refresh commodity bias (MetalMiner) → `data/micro_src/commodity_bias.json`
For each material group already in that file (steel, aluminum, copper, nickel, tin,
zinc, gold, silver, PGM, lithium, cobalt, rare earths…), call
`mcp__metalminer__ask` — one metal per question ("What is the current <metal>
price?", and "What is the industrial buying strategy for <metal>?"). Update each
group's `metalminer.signal`, `metalminer.asOf`, and append the fresh read to
`evidence`/`bias`/`score` if the signal shifted. Keep the JSON shape identical.

## 2. Refresh analyst + sentiment (TipRanks) 
`mcp__…__tipranks` / `mcp__…__ask` (TipRanks). Re-pull consensus, price target,
upside, B/H/S and SmartScore + news sentiment for the US-listed covered names
(held + recommended first, then the rest TipRanks covers). These flow into the
score via `build_universe.py` (Excel snapshot) + the deep-dive `analyst{}` blocks;
update `data/micro_src/deep_*.json` analyst fields and/or the Excel-derived fields
as available. TipRanks is US-only — foreign names keep their snapshot.

## 3. Refresh theses/evidence (Bigdata.com) → `data/micro_src/deep_r*.json`
The heavy layer. Reuse the batch lists `data/micro_src/batch_*.json` (or regenerate
by material group). Spawn ~6-7 **parallel sonnet sub-agents**, each handling ~15
names: one Bigdata smart search per name ("<Company> earnings outlook, production
and <material> price exposure in 2026", context = last two months, max_chunks 4),
writing a normalized `{ticker, held, microVerdict(bullish|bearish|neutral),
microScore 0-10, thesis, catalysts[], risks[], evidence:[{source,date,note}]}` per
name into `deep_r0.json … deep_r6.json`. Normalize verdicts, cap/flag untradable
listings (Norilsk/Moscow, Lima-only, sanctioned). If the full sweep is too heavy for
one unattended run, refresh a rotating third of the universe each day — the rest
keeps yesterday's evidence.

## 3b. AI Hedge Fund multi-analyst layer + Yahoo cross-validation

Concept ported from [virattt/ai-hedge-fund](https://github.com/virattt/ai-hedge-fund)
(MIT — reimplemented as prompt-encoded lenses, no upstream code copied). This produces
each card's **AI Hedge Fund** verdict.

- **Yahoo cross-validation pull:** run `python3 scripts/micro_yahoo.py` →
  `data/micro_src/yahoo.json`. This is an independent second source (analyst target,
  rating, margins, price) that the compiler cross-checks against FMP/TipRanks/TrueNorth.
  **Yahoo egress is often blocked in headless Claude sessions** — if this fails, the last
  committed `yahoo.json` is reused (the GitHub Action also refreshes it once/day from CI,
  where Yahoo is reachable). Google Finance has no free API, so Yahoo is the second source.
- **Persona verdicts (optional live refresh):** spawn ~14 **parallel sonnet sub-agents**,
  each handling ~15 names. Each sub-agent applies the FULL roster **in one structured pass
  per name** (not one call per persona): 4 analytical (Valuation, Fundamentals, Technicals,
  Sentiment) + 9 investor personas (Buffett, Munger, Graham, Wood, Ackman, Lynch, Burry,
  Druckenmiller, Fisher) + Risk Manager + Portfolio-Manager aggregate — reasoning over the
  data ALREADY in the pipeline (the name's `micro.json` row + `yahoo.json`), so **no
  per-name MCP call is needed**. Write a normalized `{ticker, held, aggregate:{signal,
  confidence,action,tally}, analysts:[{name,type,signal,confidence,reasoning}]}` per name
  into `hedge_r0.json … hedge_r13.json` (same shape as `deep_r*.json`; ≤1 sentence/lens to
  bound tokens). If the full sweep is too heavy for one unattended run, refresh a rotating
  third of the universe/day — the rest keeps yesterday's shard.
- **Deterministic fallback (always run):** `python3 scripts/gen_hedge_auto.py` writes
  `data/micro_src/hedge_auto.json` for all names. It sorts first in the `hedge_*.json` glob,
  so any live `hedge_r*.json` shard overrides it (same trick as `deep_auto.json`). This
  guarantees a valid, fully-populated hedgeFund layer even with no live persona run.

## 4. Refresh fundamentals (TrueNorth, quarterly) → `data/micro_src/fundamentals.json`
Only worth doing around earnings. `mcp__TrueNorth__financial_metrics` (annual,
limit 1) for US-listed names missing/stale; append trimmed fields (ebitda_margin,
net_margin, free_cash_flow_margin, roic, roe, net_debt_to_ebitda, debt_to_equity,
current_ratio, revenue_growth_yoy, ebitda_growth_yoy, earnings_per_share).

## 5. Rebuild + verify
```
python3 scripts/build_universe.py <xlsx>     # skip if xlsx absent
python3 scripts/gen_deep_auto.py             # regenerates model-derived deep-dive fillers
python3 scripts/micro_yahoo.py               # Yahoo cross-validation pull (best-effort)
python3 scripts/gen_hedge_auto.py            # regenerates AI-Hedge-Fund fallback verdicts
python3 scripts/micro_build.py               # writes data/micro.json (research + scores + hedgeFund)
```
Sanity: 204 tickers, evidence≈204/204, deep model-derived=0, fundamentals≈104,
**hedgeFund present≈204/204** (check hedge modelDerived count + any cross-val `conflict`
flags). Then `python3 scripts/micro_refresh.py` is NOT needed here (the Action owns
prices), but running it is harmless and refreshes momentum + the Yahoo cross-check.

## 6. Commit to master (data + inputs)
```
git add data/micro.json data/micro_src/ data/universe.json
git commit -m "Daily research refresh: commodity bias, analyst/sentiment, theses"
git push origin master
```
GitHub Pages redeploys on the push. Do **not** open a PR — this is a scheduled
data-only refresh to master, same as the hourly price commits.

## Notes
- Nothing is executed on the account — recommendations are analysis only.
- If MCP servers are unavailable in the fired session (auth/headless), just rebuild
  from the committed `data/micro_src/` and commit — the tab stays valid, prices stay
  live via the Action, and the next successful run refreshes the research.
