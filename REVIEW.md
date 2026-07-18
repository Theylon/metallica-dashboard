# System Review — Owner Decisions Needed

Full-system audit + fix pass, 2026-07-18 (branch `claude/system-review-data-errors-7tzido`).
Everything mechanical was fixed in that PR; the items below are **judgment calls only the
owner can make**. Tick them off and delete this file when done.

## 1. BEPC — largest position, possibly the wrong instrument ⚠

- **BEPC** (Brookfield Renewable **Corporation**) short, 31 sh ≈ −$1,051 = **9.7% of NAV** —
  ~2× the next-largest position and the **#1 risk contributor** (15.7% of portfolio risk).
- It is an off-theme renewables utility in a metals book, and `rebalance.json` (2026-07-16)
  proposed shorting **"BEP"** (Brookfield Renewable **Partners LP**) — a related but distinct
  listing. The executed size (31) also differs from the proposal (23).
- **Decide:** keep BEPC / swap to BEP / close / resize. The dashboard now tags it
  `Renewables` and the report flags it, but only you know the intent.

## 2. TSLA categorized "Lithium"

Tesla is an EV maker (a lithium *consumer*). It's currently bucketed with the lithium
miners in the Positions category filter and the scenario buckets. If it's a deliberate
theme proxy, keep; otherwise say the word and it moves to its own `EV` category
(one-line change in `scripts/mcp_refresh.py` CATEGORY).

## 3. journal.json mixes two eras

The behavioral stats (win rate 25%, profit factor 0.08, realized **−$1,162**) blend the
retired long-only lithium book (majority of trades, closed 06-22→06-30) with the current
L/S book. They are **not representative of the current strategy**. Options: label the
Journal tab with the era split, or filter the analytics to trades after 2026-06-22.

## 4. metals_spot.json sanity check

Lithium 17,441 EUR/t · Copper 13,606 USD/t · Cobalt 10.94 EUR/kg (asOf 07-16).
Copper looks high and cobalt low vs. typical levels — please eyeball against MetalMiner
before the team quotes these numbers. Also only 3 commodities are covered while the
theses lean on silver/gold/aluminum/steel spot.

## 5. linkage_map.json needs a real rebuild upstream

The equity↔commodity linkage map is signal-mined and 364/375 links fail its own
validation gates; the 11 that pass are also spurious (e.g. ALB→aluminum). `exposure.py`
now applies a family allowlist (aluminum equity can only be aluminum exposure, etc.),
which cleans the Exposure tab retroactively — but the map itself should be regenerated
with fundamental gates in metallica-fund when convenient.

## 6. Security model (action required before team rollout) ⚠

The repo is currently **public** and the dashboard password is client-side only —
anyone with the URL can fetch `data/positions.json` (and the whole git history).

1. **Now (5 min, owner action):** make the repo private + rotate the password
   (`README.md` § Security). Note the public history already contains every snapshot
   to date and the SHA-256 of the default password.
2. **Recommended follow-up PR:** encrypt `data/*.json` at deploy (AES-256-GCM, key =
   PBKDF2(passphrase) from a GitHub secret); the login password becomes the real
   decryption key. Fully implementable in-repo; kept out of the audit PR deliberately
   so auth changes don't ride along with 20 data/logic fixes.
3. **Long term:** Cloudflare Access (free tier) or Netlify password in front of the site.

## 7. report.json narrative re-blessing

The numbers in `report.json` were regenerated from live data (asOf 2026-07-18): headline,
trade tape, look-through, scenarios, benchmark comparison (SPY −0.1% / XME −14.6% since
inception — the old "+1.4%/−10.4%" was wrong), PT math (ALB ~$207/+72%, NUE $270/+14%).
The *narrative* text (drivers, catalysts, bottom line) was updated minimally to match —
worth a read-through since it speaks in your voice. Note: after the deleverage,
**precious/PGM (~20% of gross) has overtaken steel (~19%) as the largest bucket**.
