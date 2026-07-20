# System Review — Owner Decisions Needed

Two audit passes have shipped (2026-07-18 and a follow-up 2026-07-20 covering the ~13
feature PRs added since). Everything mechanical is fixed in code; the items below are
**judgment calls or owner actions only you can take**. Tick them off and delete this file
when done.

## 1. ⚠ The repo is still PUBLIC — do this first

The dashboard password is a client-side gate only; every `data/*.json` (live positions,
NAV, P&L) is directly fetchable by anyone with the URL, and the public git history holds
every snapshot to date. **Action:** make the repo private (Settings → General → Change
visibility) and rotate the dashboard password (README § Security — the default hash of
"metallica" is in public history). GitHub Pages from a private repo needs a paid plan; the
Pages site stays publicly reachable without Enterprise access control. This is unchanged
from the first review and is the single most important pre-rollout item.

## 2. BEPC — largest position, possibly the wrong instrument ⚠

**BEPC** (Brookfield Renewable **Corporation**) short, 31 sh ≈ −$1,051 = **9.7% of NAV** —
~2.6× the next-largest name and the **#1 risk contributor** (~15.5% of portfolio risk). It
is an off-theme renewables utility in a metals book, and `rebalance.json` proposed shorting
**"BEP"** (Brookfield Renewable **Partners LP**) — a related but distinct listing, at a
different size (23 vs the executed 31). **Decide:** keep BEPC / swap to BEP / close / resize.

## 3. TSLA categorized "Lithium"

Tesla is an EV maker (a lithium *consumer*), bucketed with the lithium miners in the
category filter and scenario buckets. Intentional theme proxy, or recategorize to `EV`?
(One-line change in `scripts/mcp_refresh.py` CATEGORY.)

## 4. metals_spot.json — copper/cobalt look off, and it's stale (07-17)

Copper 13,606 USD/t (~40% above plausible LME ~$9.5–10k/t); cobalt 10.94 EUR/kg (low vs the
typical $20–33k/t range). Please eyeball against MetalMiner before the team quotes these.
Only 3 commodities are covered while the theses lean on silver/gold/aluminum/steel spot.

## 5. Positioning ("Smart Money") panel is empty until fed

`positioning_build.py` is wired and its output schema matches the frontend, but
`data/positioning_src/` has only `config.json` — no FMP insider/senate/house dumps — so the
Risk/Process "Smart Money & Positioning" panels render the empty state. **Action:** run the
positioning Routine (or commit the FMP dumps) to light it up. Not a bug; just unfed.

## 6. orders.jsonl — instructionId "101" is reused across two open orders

NUE (07-19, submitted) and CLF (07-20, created) both carry instruction id "101". The tooling
now handles this safely — `order_log.set_status` prefers the newest OPEN match and warns,
`--ts` targets a specific one, and `verify_data` flags the collision — but the audit trail
is cleaner if you set NUE's real current status (its live IBKR order id is 1801196177):
`python3 scripts/order_log.py --set-status --instruction-id 101 --ts 2026-07-19 --status <filled|cancelled>`.

## 7. Security follow-up (recommended): encrypt the data at deploy

After #1, the durable fix is a follow-up PR that encrypts `data/*.json` at deploy time
(AES-256-GCM, key = PBKDF2(passphrase) from a GitHub secret) and decrypts client-side at
login, so the password becomes real protection while keeping GitHub Pages. Kept out of the
audit PRs deliberately so the auth rewrite doesn't ride along with the correctness fixes.

---

### Resolved in code by the 2026-07-20 pass (no action needed)
- **XSS**: hardened the new stock-detail modal, events/research/altdata links, and `safeUrl`
  (rejects `javascript:`, strips quotes); added modal focus-trap + `role="dialog"`.
- **CI gap**: `validate_data.py` now gates the deploy workflow (was PR-only), so a schema
  break can no longer reach the live site.
- **Stale narrative**: the Stock-Picks macro banner, sizing note, and recommendation/
  trade-list quantities now derive from the live feeds/book on every refresh (no more
  "Hawkish Fed" vs "dovish hold" contradiction, no "cover 23 of 73" against a 21-share book).
- **Journal**: labeled as the current long/short era (since 2026-06-22) with full history
  under `allTime`.
- **daily_snapshot** now prunes to a 90-day window (was unbounded git growth).
