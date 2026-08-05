# Runbook — Positioning refresh (insiders + institutional)

A fresh Claude session (scheduled Routine, fired on trading days) follows this to refresh
the **insider + institutional (smart money) channels**: raw TrueNorth dumps are committed
under `data/positioning_src/`, `scripts/positioning_build.py` normalizes them into
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
- Config: `data/positioning_src/config.json` (`windowDays`).

## 1. Insider trades (per held name)
For each ticker in `data/positions.json` (base symbol, e.g. `FCX`, `ALB` — skip ETFs and
non-US listings, which have no Form 4s):
- `mcp__TrueNorth__financial_insider_trades` — `ticker=<TKR>`, `limit=100`, and
  `start_date` = today minus `windowDays` so the dump matches the build window.
- Save the raw JSON response **verbatim** to
  `data/positioning_src/truenorth_insider_<TKR>.json`.
  Delete stale `truenorth_insider_*.json` for names no longer held.
- A `{"status": "not_found"}` response is normal — TrueNorth's Form 4 coverage is partial
  even among US listings (CLF, SCCO and MLI return not_found today while ALB and FCX
  work). Skip the name; do not save an empty dump.

## 2. Institutional ownership (13F, per held name)
- `mcp__TrueNorth__financial_institutional_ownership` — `ticker=<TKR>`, `limit=20`.
- Save verbatim to `data/positioning_src/truenorth_13f_<TKR>.json`.
- Coverage is wider than Form 4s — CLF has no insider data but 18 reporting holders — so
  run this for every held US name even when step 1 came back empty.
- The build reports the **top-N cohort's** share of outstanding, not total institutional
  ownership. Keep `limit` stable between runs, or `qoqChange` compares different cohorts.

## 3. Build + verify + commit
```
python3 scripts/positioning_build.py    # writes positioning.json + positioning_history.jsonl
python3 scripts/channel_accuracy.py     # folds the new history into the channel scorecard
python3 scripts/verify_data.py          # must stay green (process checks are WARN-only)
git add data/positioning.json data/positioning_history.jsonl data/positioning_src/ data/channel_accuracy.json
git commit -m "Positioning refresh: insiders + institutional"
git push origin master
```
GitHub Pages redeploys on push. Do **not** open a PR — scheduled data-only refresh to
master, same as the Alt-Data refresh.

## Notes
- Nothing is executed on the account — analysis only.
- Sanity per run: insider cards' technical-vs-discretionary split looks right on a spot
  check (an M/F cluster on one day = option exercise, not a bearish signal; an `A` award
  is not a buy). Watch the small-trim boundary — FCX's 2026-07-30 sale of 7,550 shares was
  9.9% of holdings and classified technical, just inside the 10% rule.
- Form 4 rows arrive with single-letter `transaction_code` and **post**-transaction
  `shares_owned_following_transaction`; `_norm_insider()` renames the keys and the
  classifier reads them directly. If TrueNorth changes that shape, `_is_form4()` drops the
  rows rather than mis-scoring them — a dump that suddenly builds 0 cards means the shape
  moved, not that insiders went quiet.
- **COT is unfed.** No connected provider serves CFTC futures positioning; `cot[]` carries
  through untouched and its Smart Money rows stay absent. Not a bug.
- **Congressional trades are no longer tracked.** The channel was never populated and the
  only structured source was an FMP endpoint behind a paid plan; re-adding it means a paid
  feed or a scraper of `efdsearch.senate.gov`.
- Scheduling: wire as a Claude Routine (CronCreate), same pattern as
  `scripts/altdata_refresh.md`; weekly is enough (Form 4s file within 2 business days, 13Fs
  quarterly with a 45-day lag).
