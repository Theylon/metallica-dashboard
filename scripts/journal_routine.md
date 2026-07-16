# Runbook — daily behavioral trade journal (Feature A)

A fresh Claude session (fired once/day on trading days by a scheduled Routine) pulls the
IBKR trade blotter and rebuilds `data/journal.json`, which powers the **Journal** tab
(win rate, profit factor, holding period, disposition effect, realized-P&L attribution,
and the "Shadow Account" — P&L left on the table by exiting).

Read-only: `get_account_trades` never places or changes an order. Analysis only.

## 0. Prereqs
- Work on `master` (data-only change, like the hourly refresh):
  `git fetch origin master && git checkout master && git pull`.
- Run this **after** the IBKR/MCP refresh so `data/positions.json` (used for the Shadow
  Account's current prices) is fresh. If `data/price_history.json` exists (the Action
  writes it), fully-exited names also get a current mark from it.

## 1. Pull the trade blotter → `/tmp/ibkr_trades.json`
Call `get_account_trades` with `period="YEAR_TO_DATE"` and save the raw JSON **verbatim**
to `/tmp/ibkr_trades.json`. YTD covers the whole account (inception 2026-06-10), so every
fill is captured and the FIFO round-trip matcher starts clean.

> Year-boundary caveat: in a future January, `YEAR_TO_DATE` no longer reaches prior-year
> fills. When that matters, switch to a rolling window that spans inception (e.g.
> `DAYS_90` accumulated) or add a persistent closed-trip ledger. Fine as-is for now.

## 2. Rebuild + verify
```
python3 scripts/journal.py     # /tmp/ibkr_trades.json → data/journal.json
```
`journal.py` FIFO-matches fills into closed round-trips (handles partial fills and short
sell-to-open first), computes the aggregates + attribution + Shadow Account, and prints a
one-line summary. If the dump is missing/empty it leaves `data/journal.json` untouched
(so the tab never blanks). Sanity: `closedTrades` > 0, `winRate` in [0,1], `profitFactor`
finite, `dispositionEffect` reported in days.

## 3. Commit to master
```
git add data/journal.json
git commit -m "Daily trade journal refresh"
git push origin master
```
GitHub Pages redeploys on the push. Do **not** open a PR — scheduled data-only refresh to
master, same as the hourly price commits.

## Notes
- Nothing is executed on the account.
- If the IBKR MCP is unavailable in the fired session, skip — the tab keeps its last-good
  `journal.json` and the next successful run refreshes it.
