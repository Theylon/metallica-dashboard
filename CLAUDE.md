# CLAUDE.md — working agreement for this repo

This file is the standard. Read it before you change anything; it carries the
conventions so you (human or agent) don't have to hold them in your head. It is
loaded automatically at the start of every Claude Code session.

If something here is wrong or out of date, fix **this file** in the same PR —
the standard lives in the repo, not in memory.

---

## What this is

A password-gated GitHub Pages dashboard for the **Metallica** systematic
long/short metals-equity strategy. It shows live IBKR positions, NAV/P&L, and
benchmark comparisons, plus a "Stock Picks" research tab over a ~204-name
universe. There is **no backend** — the browser fetches static `data/*.json`
files that a pipeline regenerates and commits.

```
IBKR Web API / Yahoo / research  ──▶  scripts/*.py  ──▶  data/*.json  ──▶  index.html (GitHub Pages)
                                                          (committed)      (fetches JSON in-browser)
```

## Map of the repo

| Path | Role |
|------|------|
| `index.html` | The entire dashboard — all HTML/CSS/JS inline. Fetches `data/*.json`. |
| `scripts/fetch.py` | Primary fetcher (IBKR + Yahoo). Runs in the deploy Action. |
| `scripts/mcp_refresh.py` | Rebuilds `positions/account/pnl/benchmarks.json` from raw IBKR MCP dumps in `/tmp`. Used by the SessionStart auto-refresh. |
| `scripts/enrich.py` | Builds `commodities/analysts/macro/news.json`. |
| `scripts/micro_*.py`, `gen_*.py`, `build_universe.py` | Stock Picks pipeline → `data/micro.json` from `data/micro_src/`. |
| `scripts/validate_data.py` | **Data-contract validator** (see below). |
| `scripts/check.sh` | One-command local standards gate. |
| `scripts/trade_gate.py` | **Pre-trade risk gate** — deterministic checks before any IBKR order instruction (see Trading below). |
| `scripts/order_log.py` | Append-only order audit trail → `data/orders.jsonl`. |
| `.claude/skills/trade/SKILL.md` | The `/trade` skill — the guarded execution workflow a session follows. |
| `data/*.json` | Machine-generated dashboard inputs. |
| `data/report.json` | **Static** hand-authored strategy report. Not written by any refresh script. |
| `scripts/daily_snapshot.py` | Freezes every live `data/*.json` verbatim into `history/daily/<date>.json.gz` on each refresh (converges to EOD) for later analysis. Kept outside `data/` so Pages doesn't ship the archive. |
| `history/daily/` | The per-day full-data snapshots (gzipped JSON). Immutable once the day passes. |
| `.github/workflows/fetch-data.yml` | Scheduled fetch + Pages deploy (owns `master`). |
| `.github/workflows/standards.yml` | Standards gate on PRs / working branches. |
| `.claude/hooks/session-start.sh` | Injects the IBKR auto-refresh directive on web sessions. |

## The data contract (most important thing to protect)

`index.html` fetches these files and reads specific keys out of them. There is
no server and no schema enforcement in the browser — **a dropped key or a blank
file just silently breaks a tab in production.** So the contract is enforced in
code instead:

> `python scripts/validate_data.py` — validates every dashboard-consumed file's
> shape (required keys, row shapes, benchmark array lengths, valid JSON). CI runs
> it on every PR; run it yourself after any change under `data/` or `scripts/`.

Files the dashboard depends on: `positions, account, pnl, benchmarks, report,
commodities, analysts, macro, news, technicals, metals_spot, research, micro`.

Rules of thumb:
- **Add keys freely; never rename or remove one** the dashboard reads without
  updating `index.html` in the same change.
- If you add a new `data/*.json` the dashboard consumes, add its contract to
  `SPECS` in `validate_data.py`.
- **`data/report.json` is static content.** No refresh script may write it.
  `mcp_refresh.py` explicitly leaves `report.json` (and, per the auto-refresh
  directive, `benchmarks.json`) untouched.

## Security — non-negotiable

- **The repo stays private.** `data/*.json` holds live position data and is
  directly fetchable; the `index.html` password is only a client-side gate.
  Do not make the repo public to get free Pages — private Pages needs a paid plan.
- **Never commit secrets.** The IBKR OAuth **private key**, consumer key, and
  account id live only in GitHub Actions secrets (`IBKR_PRIVATE_KEY`,
  `IBKR_CONSUMER_KEY`, `IBKR_ACCOUNT_ID`). No `.pem`/`.key`/`.env` in git. The
  secret guard in `check.sh` / `standards.yml` blocks the obvious cases.
- The client-side password hash in `index.html` **is** fine to commit — it's the
  gate itself, not a secret.

## How refreshes work (and how to keep them safe)

- **Scheduled:** `fetch-data.yml` runs 4×/day on market days, commits fresh
  `data/`, and deploys Pages. Any push to `master` redeploys.
- **Session auto-refresh:** on web sessions the SessionStart hook asks the agent
  to pull the IBKR MCP, run `mcp_refresh.py`, and land a data-only commit on
  `master`. This is the one sanctioned direct-to-`master` path.
- **Stock Picks research:** rebuilt once/day pre-market by a Claude Routine
  (`scripts/micro_refresh_research.md`); prices refresh 4×/day in the Action.

Refresh-script invariants:
- **Idempotent** — running twice produces the same file, not duplicated rows.
- **Never regress fresher data.** Before pushing a refresh to `master`, confirm
  your data is newer than what's there (compare `updatedAt`). A stale overwrite
  is worse than no refresh.
- **Degrade, don't blank.** On a missing/errored input, keep the last-good value
  (as `mcp_refresh.build_benchmarks` does) rather than writing an empty file.

## Trading — how an order leaves a Claude session

Execution runs through **IBKR order instructions** (the IBKR MCP's
`create_order_instruction`): the session prepares the ticket, IBKR requires the
owner to open the returned deep-link and submit it in the IBKR app. Claude
prepares, the owner executes. The full workflow lives in
`.claude/skills/trade/SKILL.md`; the rules that never bend:

- **Only trade what the owner asked for in the session** — no unprompted or
  autonomous orders, one order at a time, each explicitly confirmed.
- **Every ticket passes `scripts/trade_gate.py`** (sizing, exposure,
  fat-finger, earnings-window rule 4a, macro-bias rule 4e). A FAIL blocks
  unless the owner overrides that named gate; overrides are logged.
- **Every instruction is recorded** in `data/orders.jsonl` via
  `scripts/order_log.py` (created → submitted → filled/cancelled), including
  its **trigger** (owner ask / recommendation / rebalance row / alert) and the
  owner's **reason** — and, once filled, the actual **fill price** plus
  look-back **outcomes** (+1d/+5d/+30d forward returns,
  `order_log.py --update-outcomes`, backfilled by the fetch Action). Statuses
  must reflect live IBKR state — reconcile against `get_account_orders` /
  `get_account_trades`, don't leave stale `created` rows. The dashboard's
  **Orders tab** renders it read-only;
  every line must parse (`validate_data.py`'s JSONL step) — semantic checks
  stay warn-only in `verify_data.py`.
- **After fills, refresh** (`mcp_refresh.py` flow) so the dashboard shows the
  real book. `orders.jsonl` commits are data-only → straight to `master` is fine.

## Coding conventions

- Python 3.11, **standard-library first.** Runtime deps are only `requests`,
  `yfinance`, `cryptography` (installed in the Action). Keep tooling scripts
  (`validate_data.py`) dependency-free so they run anywhere.
- Every script starts with `#!/usr/bin/env python3` and a docstring saying what
  it reads and writes. Match the surrounding style.
- Write JSON with `json.dump(..., indent=2)`; timestamps are UTC ISO-8601
  (`updatedAt` / `asOf`).
- `ruff` is advisory here (it flags some pre-existing style debt); don't let it
  block a data fix, but don't add new findings either.

## Workflow — how a change reaches production

1. Branch from `master` (`claude/<topic>` is the convention).
2. Make the change. **Run `./scripts/check.sh`** — it must be green.
3. If you touched `index.html` or a script's output, **verify in the real app**:
   `python3 -m http.server 8000` and load the dashboard, don't just eyeball JSON.
4. Open a **draft PR** into `master`; fill in the PR template. The Standards
   workflow runs the gate automatically.
5. Merge to `master` → the deploy Action publishes Pages at
   <https://theylon.github.io/metallica-dashboard/>.

Data-only refreshes may go straight to `master` (that's what the scheduler and
the auto-refresh hook do). **Code changes go through a PR** — never push
`index.html`/`scripts/` changes directly to `master`.

## Before you finish

- `./scripts/check.sh` is green.
- No secrets in the diff (`git diff --staged`).
- Data contract intact; `report.json` untouched unless that was the task.
- Dashboard still renders the tabs you touched.
