# Metallica Dashboard

Password-protected GitHub Pages dashboard for the Metallica systematic L/S equity strategy. Shows live IBKR positions, P&L (hourly/daily/weekly), and benchmark comparisons.

## Setup

### 1. Create the GitHub repo

```bash
gh repo create metallica-dashboard --private --source=. --remote=origin --push
```

> **Recommend: private repo** — the `data/` JSONs contain live position data.

### 2. Enable GitHub Pages

Deployment is handled by the **Fetch IBKR Data & Deploy** GitHub Action (it builds
and publishes the site on every data refresh). The workflow auto-enables Pages on its
first run, so you usually don't need to touch any settings. If it doesn't, set it
manually: **Settings → Pages → Source → GitHub Actions**.

Your dashboard will be at: `https://<your-username>.github.io/metallica-dashboard/`

> **Private repo note:** GitHub Pages on a **private** repository requires a paid plan
> (Pro/Team/Enterprise). The dashboard password is a client-side gate only — the
> `data/*.json` files are directly fetchable — so do **not** make this repo public to
> get free Pages, or you'll expose live position data. Keep it private + paid.

### 3. Add GitHub Secrets

Go to **Settings → Secrets and variables → Actions** and add:

| Secret | Value |
|--------|-------|
| `IBKR_CONSUMER_KEY` | Your IBKR OAuth consumer key |
| `IBKR_PRIVATE_KEY` | RSA private key PEM (paste the full `-----BEGIN RSA PRIVATE KEY-----...` block) |
| `IBKR_ACCOUNT_ID` | Your account number (e.g. `U1234567`) |

> The IBKR Web API uses OAuth 1.0a with RSA-SHA256. Generate a key pair, register the public key with IBKR, and paste the private key as the `IBKR_PRIVATE_KEY` secret.

### 4. Change the dashboard password

The default password is `metallica`. To change it:

```bash
echo -n "yournewpassword" | shasum -a 256
```

Copy the hash, then edit `index.html` and replace the value of `PASSWORD_HASH` near the top of the `<script>` block:

```js
const PASSWORD_HASH = 'paste-your-new-hash-here';
```

### 5. Test locally

```bash
pip install requests yfinance cryptography

export IBKR_CONSUMER_KEY="your-key"
export IBKR_PRIVATE_KEY="$(cat your-private-key.pem)"
export IBKR_ACCOUNT_ID="U1234567"

python scripts/fetch.py
```

Then open `index.html` in a browser (or run `python3 -m http.server 8000`).

### 6. Trigger first data fetch

Go to **Actions → Fetch IBKR Data → Run workflow** to trigger manually and confirm everything works before waiting for the cron.

## Data refresh

The GitHub Action runs every **30 minutes** Monday–Friday 9am–4pm ET. It:

1. Calls the IBKR Web API for positions, NAV, and P&L
2. Fetches 90-day benchmark closes (SPY, XME, SLV, CPER, JJU) from Yahoo Finance
3. Appends a timestamped snapshot to `data/pnl.json`
4. Commits and pushes the updated `data/` files

The dashboard auto-refreshes every 5 minutes from the browser.

## Benchmarks

| Ticker | What it represents |
|--------|--------------------|
| SPY    | S&P 500 |
| XME    | SPDR Metals & Mining ETF |
| SLV    | Silver |
| CPER   | Copper ETF |
| JJU    | Aluminum ETF (iPath) |

## Files

```
├── index.html                  # Dashboard (single file, all CSS/JS inline)
├── scripts/fetch.py            # Data fetcher — IBKR + Yahoo Finance
├── .github/workflows/
│   └── fetch-data.yml         # Scheduled cron pipeline
└── data/
    ├── positions.json          # Current positions (updated each fetch)
    ├── account.json            # NAV, exposure, P&L summary
    ├── pnl.json                # Rolling 90-day P&L history (hourly snapshots)
    └── benchmarks.json         # Benchmark daily closes + today's intraday
```

## Stock Picks — micro-analysis & AI Hedge Fund layer

The **Stock Picks** tab scores a ~204-name universe (0-100 composite) and expands each
name into a research card. Its data (`data/micro.json`) is built offline from committed
inputs in `data/micro_src/` by `scripts/micro_build.py`, refreshed daily by a Claude
research Routine (`scripts/micro_refresh_research.md`) and 4×/day for prices by the
Action (`scripts/micro_refresh.py`).

Each card also carries an **AI Hedge Fund** multi-analyst verdict — concept ported from
[virattt/ai-hedge-fund](https://github.com/virattt/ai-hedge-fund) (MIT; no upstream code
copied). A full roster (4 analytical agents + 9 investor personas + risk/portfolio
manager) gives each name a bullish/bearish/neutral signal, conviction, and an aggregate
action. It is **display-only** (does not change the composite). A deterministic fallback
(`scripts/gen_hedge_auto.py`) keeps all names populated even without a live research run.
An independent **Yahoo Finance** pull (`scripts/micro_yahoo.py`, `yfinance`) cross-checks
analyst targets, ratings and margins against the primary sources and flags divergences.

```
scripts/
├── micro_build.py          # compiler → data/micro.json (composite + hedgeFund + cross-val)
├── micro_refresh.py        # 4×/day price/score refresh (Action); recomputes Yahoo cross-check
├── gen_hedge_auto.py       # deterministic AI-Hedge-Fund fallback → data/micro_src/hedge_auto.json
├── micro_yahoo.py          # Yahoo Finance cross-validation pull → data/micro_src/yahoo.json
└── micro_refresh_research.md   # daily research Routine runbook
data/micro_src/
├── hedge_auto.json         # fallback verdicts (hedge_r*.json research shards override it)
└── yahoo.json              # independent Yahoo pull (generated in CI; not always committed)
```

## Strategy reference

Metallica is a systematic long/short equity strategy powered by MetalMiner's proprietary industrial-metals price data.

| Metric | OOS Value |
|--------|-----------|
| Sharpe | 1.48 |
| CAGR | 25.4% |
| Max Drawdown | −18.0% |
| Avg β to S&P 500 | 0.20 |
| OOS Window | Jan 2022 – Jun 2026 (4.5 yr) |
