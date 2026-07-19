# Contributing

The engineering standards for this repo live in **[`CLAUDE.md`](CLAUDE.md)** —
architecture, the data contract, security rules, and conventions. It's the
source of truth for both humans and AI sessions. This page is the short version
for getting set up and shipping a change.

## Setup

```bash
pip install requests yfinance cryptography   # runtime deps (data pipeline)
pip install ruff                             # optional: advisory lint
```

Serve the dashboard locally (it's a static site — just open `index.html` over HTTP):

```bash
python3 -m http.server 8000
# → http://localhost:8000/index.html   (default password: metallica)
```

## The one command to remember

```bash
./scripts/check.sh
```

Runs the same gate as CI: compiles the scripts, validates the `data/` contract,
and scans for committed secrets. **Green here means green in CI.** Run it before
every PR. To check just the data contract:

```bash
python3 scripts/validate_data.py
```

## Shipping a change

1. Branch from `master` (`claude/<topic>` is the convention).
2. Make the change; keep the [data contract](CLAUDE.md#the-data-contract-most-important-thing-to-protect)
   intact and **never commit secrets**.
3. `./scripts/check.sh` → green. If you touched `index.html` or a script's
   output, load the dashboard and confirm the affected tab renders.
4. Open a **draft PR** into `master` and fill in the template. The **Standards**
   workflow runs the gate on your PR automatically.
5. On merge, the deploy Action publishes to GitHub Pages.

**Code changes (`index.html`, `scripts/`) go through a PR.** Only data-only
refreshes go straight to `master` — that's what the scheduler and the SessionStart
auto-refresh hook do.

## What CI enforces

| Check | Blocking? | What it protects |
|-------|-----------|------------------|
| `py_compile scripts/*.py` | yes | scripts are at least syntactically valid |
| `validate_data.py` | yes | the dashboard's JSON contract holds |
| secret guard | yes | no private keys / `.env` reach the repo |
| `ruff` | advisory | style — surfaced, never blocks a data fix |

See `.github/workflows/standards.yml`.
