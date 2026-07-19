# Metallica Dashboard

Password-protected GitHub Pages dashboard for the Metallica systematic L/S equity strategy. Shows live IBKR positions, P&L, and benchmark comparisons.

## Development workflow & standards

Engineering standards live in the repo so the workflow carries them for us —
you don't have to remember them, and CI won't let a break through:

- **[`CLAUDE.md`](CLAUDE.md)** — the working agreement: architecture, the data
  contract, security rules, and conventions. Read first (loaded into every
  Claude Code session automatically).
- **[`CONTRIBUTING.md`](CONTRIBUTING.md)** — how to set up and ship a change.
- **`./scripts/check.sh`** — one local command that runs the same gate as CI
  (data-contract validation, script compile, secret guard). Run it before every PR.
- **Standards CI** (`.github/workflows/standards.yml`) — runs that gate on every
  PR and working-branch push. The [PR template](.github/pull_request_template.md)
  mirrors the checklist.

The load-bearing invariant is the **data contract**: `index.html` fetches static
`data/*.json` with no server to catch a bad shape, so
[`scripts/validate_data.py`](scripts/validate_data.py) encodes and enforces it.

## ⚠ Security — read before adding users

The dashboard password is a **client-side gate only**. The `data/*.json` files are
served by GitHub Pages and directly fetchable by anyone with the URL, password or not,
and a public repo additionally exposes the full git history of every position snapshot.

1. **Now:** keep the repo **private** (Settings → General → Danger Zone → Change
   visibility) and rotate the dashboard password (see below). GitHub Pages on a private
   repo requires a paid plan (Pro/Team/Enterprise); the Pages *site* itself remains
   publicly reachable unless you're on Enterprise access control.
2. **Next (recommended):** encrypt `data/*.json` at deploy time (AES-GCM with a key
   derived from the dashboard passphrase via PBKDF2, passphrase in a GitHub secret) and
   decrypt client-side at login — this makes the password real protection while keeping
   GitHub Pages. Planned as a follow-up PR; see REVIEW.md.
3. **Long term:** host behind real auth (Cloudflare Access has a free tier, or Netlify
   password protection).

## Setup

### 1. Create the GitHub repo

```bash
gh repo create metallica-dashboard --private --source=. --remote=origin --push
```

### 2. Enable GitHub Pages

Deployment is handled by the **Refresh Derived Data & Deploy** GitHub Action (it builds
and publishes the site on every data refresh). The workflow auto-enables Pages on its
first run, so you usually don't need to touch any settings. If it doesn't, set it
manually: **Settings → Pages → Source → GitHub Actions**.

Your dashboard will be at: `https://<your-username>.github.io/metallica-dashboard/`

### 3. Change the dashboard password

The default password is `metallica`. To change it:

```bash
echo -n "yournewpassword" | shasum -a 256
```

Copy the hash, then edit `index.html` and replace the value of `PASSWORD_HASH` near the top of the `<script>` block:

```js
const PASSWORD_HASH = 'paste-your-new-hash-here';
```

### 4. Test locally

No secrets needed — the committed `data/` files are the state:

```bash
python3 -m http.server 8000   # then open http://localhost:8000
```

To sanity-check the data before serving: `python3 scripts/verify_data.py`.

## Data refresh — two layers

**IBKR book data** (`positions/account/pnl/benchmarks.json`) is refreshed by the **MCP
pipeline**: a Claude session (SessionStart hook or scheduled Routine) calls the IBKR MCP
tools, saves the raw results to `/tmp`, and runs `scripts/mcp_refresh.py`, which rewrites
the four files, then recomputes exposure + risk. Commits land on `master`, which triggers
a deploy.

**Derived layers** are refreshed by the GitHub Action **4×/day** on trading days
(~09:30 / 12:00 / 14:00 / 15:55 ET): Yahoo cross-validation, Stock-Picks prices/scores
(`micro_refresh.py`), risk metrics (`risk.py`), and the signal scorecard (`signal_ic.py`).
Before committing, the Action runs `scripts/verify_data.py` — a cross-file consistency
gate (account↔positions identities, pnl schema, benchmark set, micro book vs live book).
**A failed check fails the run and nothing deploys.**

The dashboard auto-refreshes every 5 minutes from the browser.

## Benchmarks

| Ticker | What it represents |
|--------|--------------------|
| SPY    | S&P 500 |
| XME    | SPDR Metals & Mining ETF |
| SLV    | Silver |
| CPER   | Copper ETF |

## Files

```
├── index.html                  # Dashboard (single file, all CSS/JS inline)
├── scripts/
│   ├── mcp_refresh.py          # IBKR book refresh (from MCP dumps in /tmp)
│   ├── verify_data.py          # cross-file consistency gate (run by the Action pre-deploy)
│   ├── risk.py · exposure.py · journal.py · signal_ic.py · enrich.py
│   ├── channel_accuracy.py · decision_log.py · alerts_build.py · positioning_build.py
│   │                           # Process layer (see PROCESS.md + the Process tab)
│   └── micro_*.py              # Stock Picks pipeline (see below)
├── .github/workflows/
│   └── fetch-data.yml          # derived-data refresh + verify + deploy (4×/day cron)
└── data/
    ├── positions.json          # Current positions (updated each MCP refresh)
    ├── account.json            # NAV, exposure, P&L summary (reconciles to positions)
    ├── pnl.json                # NAV + TWR history since inception (+ today's intraday)
    └── benchmarks.json         # Benchmark daily closes
```

> `data/universe.json` still carries a `held` overlay from its original Excel build; it
> is **superseded** — `micro_build.py`/`micro_refresh.py` overlay held/heldMv/position
> straight from `positions.json` on every run.

## Stock Picks — micro-analysis & Yahoo cross-check

The **Stock Picks** tab scores a ~204-name universe (0-100 composite) and expands each
name into a research card. Its data (`data/micro.json`) is built offline from committed
inputs in `data/micro_src/` by `scripts/micro_build.py`, refreshed daily by a Claude
research Routine (`scripts/micro_refresh_research.md`) and 4×/day for prices by the
Action (`scripts/micro_refresh.py`).

Each card also carries an independent **Yahoo Finance** data cross-check
(`scripts/micro_yahoo.py`, `yfinance`): it pulls analyst targets, ratings and margins
from a second source and flags where they diverge from the primary FMP/TipRanks/TrueNorth
numbers. It is **display-only** (does not change the composite).

```
scripts/
├── micro_build.py          # compiler → data/micro.json (composite + Yahoo cross-check)
├── micro_refresh.py        # 4×/day price/score refresh (Action); recomputes Yahoo cross-check
├── micro_yahoo.py          # Yahoo Finance cross-validation pull → data/micro_src/yahoo.json
└── micro_refresh_research.md   # daily research Routine runbook
data/micro_src/
└── yahoo.json              # independent Yahoo pull (generated in CI; not always committed)
```

## Research & risk analytics

Four research layers (inspired by [HKUDS/Vibe-Trading](https://github.com/HKUDS/Vibe-Trading)) deepen the dashboard beyond raw account data. Each is additive, resilient (a missing input leaves the last-good file in place), and never overwrites the hand-authored `report.json`.

| Tab | What it shows | Data file | Built by | Cadence |
|---|---|---|---|---|
| **Risk** (extended) | Auto-computed vol / β(SPY,XME) / VaR / HHI, plus a live **correlation heatmap** and per-name **risk contribution** (component VaR) | `data/risk.json` | `scripts/risk.py` (pure Python) | Action 4×/day + MCP refresh |
| **Journal** | Behavioral trade analytics — win rate, profit factor, holding period, **disposition effect**, realized-P&L attribution, and a **Shadow Account** (P&L left on the table by exiting) | `data/journal.json` | `scripts/journal.py` ← `get_account_trades` | daily Journal routine (`scripts/journal_routine.md`) |
| **Orders** | Read-only audit trail of every IBKR **order instruction** placed via `/trade` — status chain created → submitted → filled/cancelled, the **trigger** (owner / recommendation / rebalance / alert), the owner's **reason**, gate results, and a **submit deep-link** for pending tickets (opens IBKR Mobile) | `data/orders.jsonl` | `scripts/order_log.py` (written by the `/trade` workflow) | on demand, per `/trade` session |
| **Signals** | **IC/IR scorecard** — which of the 8 micro sub-scores actually predict forward returns — plus the book's **factor tilt** (momentum/value/quality/size/low-vol) | `data/signal_scorecard.json` (+ `data/micro_history.jsonl` history) | `scripts/signal_ic.py`; snapshots via `scripts/micro_snapshot.py` | Action 4×/day (scorecard turns on after ~25 days) |
| **Intel** (extended) | Per-holding **sentiment + next earnings + news** for the whole book, auto **positioning** (13F/insider/COT, feeds the Risk tab's Smart-Money panel), and a **macro-regime** series | `events.json`, `positioning.json`, `macro_history.json` | `scripts/enrich.py` builders | daily research routine (`scripts/micro_refresh_research.md` §5b) |
| **Process** | **Channel accuracy** (MedAE / hit-rate per data channel, ≥80% trust gate), the auto-written **decision & trigger log** with +30/+90-day outcome review, **insider (discretionary vs technical) + politician** trades, hard-rule cards and **pre-earnings alerts** (also shown as an Overview banner) | `channel_accuracy.json`, `decision_log.jsonl`, `alerts.json`, `positioning.json` | `scripts/channel_accuracy.py`, `scripts/decision_log.py` (hooked into the micro pipeline), `scripts/alerts_build.py`, `scripts/positioning_build.py` | Action 4×/day; insider/politician dumps via `scripts/positioning_refresh.md` Routine. Methodology: **PROCESS.md** |

Pure-Python pieces (`risk.py`, `signal_ic.py`, `micro_snapshot.py`, price-history capture in `micro_refresh.py`) run in the GitHub Action from data that already exists — no new secrets. The MCP-fed pieces (Journal, Intel research layer) run in scheduled Claude routines and degrade gracefully until first populated. `data/price_history.json` (held-name close series, reused from the existing `micro_refresh.py` download) gates the correlation matrix and the low-vol factor.

## Trading from a Claude session

The account is traded directly from a Claude session through **IBKR order
instructions** (`.claude/skills/trade/SKILL.md`): the session sizes the ticket
against live account data, runs it through the deterministic pre-trade gate
(`scripts/trade_gate.py` — sizing / exposure / fat-finger / earnings-window /
macro-bias checks), gets the owner's explicit confirmation, creates the
instruction via the IBKR MCP, and logs it to `data/orders.jsonl`
(`scripts/order_log.py`). IBKR requires the owner to submit the instruction in
its own app — Claude prepares, the owner executes. The dashboard's **Orders**
tab renders the audit trail, with a submit deep-link for pending instructions.
Details: PROCESS.md §7.

## Alt-Data tab — M Science-style nowcast & research

The **Alt-Data** tab ports the alternative-data research *method* used by desks like M Science
(pre-earnings **KPI nowcast vs. consensus**, a **track record** of estimate/consensus vs.
reported, **driver drill-down**, and a concise analyst **narrative**) — fed by our **own** live
feeds, never by redistributing anyone's proprietary report.

Two sub-tab groups:

- **Book · Metals** — the held names, with a metals-relevant mosaic (MetalMiner physical
  prices/buying-strategy, inventories/premiums, EV/battery & China demand, Bigdata sentiment).
- **Watchlist · Consumer/TMT** — the consumer/TMT names where card-spend / web-traffic panels
  make a real nowcast feasible (NKE, AFRM, CMG, LYFT, UBER, DASH, ABNB, ONON, DECK, CROX, BIRK, SBUX).

| Item | Source | Notes |
|---|---|---|
| Data file | `data/altdata.json` (`{updatedAt, counts, items}`) | built from committed inputs; resilient |
| Config | `data/altdata_src/watchlist.json` | watchlist + KPI mapping + metal→driver map |
| Research shards | `data/altdata_src/alt_r*.json` | narratives, trends, nowcast, track record (higher shard wins) |
| Builder | `scripts/altdata_build.py` (pure Python) | book group derived from `positions.json`; auto-defaults keep the tab populated |
| Refresh routine | `scripts/altdata_refresh.md` | scheduled Claude Routine → CarbonArc / MetalMiner / Bigdata.com / FMP·TipRanks / web, commits data-only to `master` |

Sourcing is **live MCP + web only** — no automated inbox/Drive ingestion, and no third-party
report text is committed (those feeds are licensed to the user personally). Like the other
research layers it is additive and degrades gracefully (a missing input leaves the last-good
file in place; `report.json`/`benchmarks.json` are never touched).

## Strategy reference

Metallica is a systematic long/short equity strategy powered by MetalMiner's proprietary industrial-metals price data.

| Metric | OOS Value |
|--------|-----------|
| Sharpe | 1.48 |
| CAGR | 25.4% |
| Max Drawdown | −18.0% |
| Avg β to S&P 500 | 0.20 |
| OOS Window | Jan 2022 – Jun 2026 (4.5 yr) |
