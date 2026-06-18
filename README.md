# Metallica Dashboard

Password-protected GitHub Pages dashboard for the Metallica systematic L/S equity strategy. Shows live IBKR positions, P&L (hourly/daily/weekly), and benchmark comparisons.

## Setup

### 1. Create the GitHub repo

```bash
gh repo create metallica-dashboard --private --source=. --remote=origin --push
```

> **Recommend: private repo** — the `data/` JSONs contain live position data.

### 2. Enable GitHub Pages

Go to **Settings → Pages → Source** and set:
- Branch: `main`
- Folder: `/ (root)`

Your dashboard will be at: `https://<your-username>.github.io/metallica-dashboard/`

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

## Strategy reference

Metallica is a systematic long/short equity strategy powered by MetalMiner's proprietary industrial-metals price data.

| Metric | OOS Value |
|--------|-----------|
| Sharpe | 1.48 |
| CAGR | 25.4% |
| Max Drawdown | −18.0% |
| Avg β to S&P 500 | 0.20 |
| OOS Window | Jan 2022 – Jun 2026 (4.5 yr) |
