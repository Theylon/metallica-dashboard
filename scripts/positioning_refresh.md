# Runbook — Positioning refresh (insiders + politicians)

A fresh Claude session (scheduled Routine, fired on trading days) follows this to refresh
the **insider + politician (smart money) channels**: raw FMP dumps are committed under
`data/positioning_src/`, `scripts/positioning_build.py` normalizes them into
`data/positioning.json` (Risk tab "Smart Money" + Process tab panels) and appends the
daily signal rows `channel_accuracy.py` scores the channels from.

The qualitative rule this feeds (codified in the build script, documented in PROCESS.md):
**an open-market insider BUY is always a signal** ("many reasons to sell, only one reason
to buy"); a SELL only counts when it is *discretionary* — RSU/10b5-1/option-exercise/small
trims are classified technical and excluded from the signal.

## 0. Prereqs
- Work on `master` (`git fetch origin master && git checkout master && git pull`). Data-only.
- A plain `python3 scripts/positioning_build.py` with no new dumps leaves
  `data/positioning.json` untouched, so every MCP step below is best-effort.
- Config: `data/positioning_src/config.json` (`windowDays`, `trackedPoliticians`).

## 1. Insider trades (per held name)
For each ticker in `data/positions.json` (base symbol, e.g. `CLF`, `TSLA` — skip ETFs and
non-US listings FMP won't have Form 4s for):
- `mcp__FMP__insiderTrades` — endpoint `insider-trading` (symbol=<TKR>, limit≈100).
- Save the raw JSON response **verbatim** to `data/positioning_src/fmp_insider_<TKR>.json`.
  Delete stale `fmp_insider_*.json` for names no longer held.

## 2. Politician / congressional trades
- `mcp__FMP__senate` — senate-trades feed → save verbatim to
  `data/positioning_src/fmp_senate.json`.
- `mcp__FMP__senate` — house-disclosure feed → save verbatim to
  `data/positioning_src/fmp_house.json`.
- Save the **full** feeds — the build script filters to universe/watchlist tickers plus any
  name matching `trackedPoliticians`, so no pre-filtering in the session.
- First run: confirm the response field names match what `positioning_build.py` expects
  (`symbol/ticker`, `type`, `amount`, `transactionDate`, `disclosureDate`,
  `representative`/`firstName`+`lastName`) and extend its `_first(...)` aliases if FMP's
  shape differs.

## 3. (Optional) 13F / COT
`mcp__FMP__form13F` and `mcp__FMP__commitmentOfTraders` dumps can be saved as
`fmp_13f_<TKR>.json` / `fmp_cot_<key>.json` for a future institutional/COT normalizer —
the build script currently carries the existing `institutional[]`/`cot[]` through untouched.

## 4. Build + verify + commit
```
python3 scripts/positioning_build.py    # writes positioning.json + positioning_history.jsonl
python3 scripts/channel_accuracy.py     # folds the new history into the channel scorecard
python3 scripts/verify_data.py          # must stay green (process checks are WARN-only)
git add data/positioning.json data/positioning_history.jsonl data/positioning_src/ data/channel_accuracy.json
git commit -m "Positioning refresh: insiders + politicians"
git push origin master
```
GitHub Pages redeploys on push. Do **not** open a PR — scheduled data-only refresh to
master, same as the Alt-Data refresh.

## Notes
- Nothing is executed on the account — analysis only.
- Sanity per run: every held US name has an `fmp_insider_*.json`; `politicians[]` rows have
  sane `disclosureLagDays` (0–90); insider cards' technical-vs-discretionary split looks
  right on a spot check (an M/F cluster on one day = option exercise, not a bearish signal).
- If FMP's plan gates an endpoint, skip it — the build degrades gracefully and the next
  successful run refreshes coverage.
- Scheduling: wire as a Claude Routine (CronCreate), same pattern as
  `scripts/altdata_refresh.md`; weekly is enough (Form 4s file within 2 business days,
  congressional disclosures lag up to 45 days).
