---
name: trade
description: >
  Place, cancel, or check an order on the live IBKR account from a Claude
  session — the guarded execution workflow (gate → owner confirmation → order
  instruction → log). Use whenever the owner asks to buy, sell, short, cover,
  trim, add, close, or hedge a position, or to place/cancel/check an order —
  in any language (קנה, מכור, שורט, כסה, סגור פוזיציה, בטל הוראה, מה סטטוס
  ההוראה). Not for research/analysis-only questions.
---

# /trade — guarded IBKR execution from a Claude session

This repo's live account is traded through **IBKR order instructions**: the
session prepares the full ticket and creates an *instruction* via the IBKR MCP;
IBKR then requires the **owner to open the returned deep-link and tap Submit**
in the IBKR app/portal before anything reaches the market. Claude prepares,
the owner executes — that two-step is a feature, not a limitation. Never claim
an order was placed; say an *instruction* was created and link the URL.

## Invariants (non-negotiable)

1. **Only trade what the owner asked for in this session.** No unprompted
   trades, no "while I'm at it" adds, no autonomous trading from Routines.
2. **One order at a time**, each with its own gate run and its own explicit
   confirmation of the exact ticket (side, qty, ticker, type, limit, TIF).
3. **Every ticket runs `scripts/trade_gate.py` first.** A FAIL gate blocks the
   order unless the owner explicitly overrides that *named* gate; rerun with
   `--override <gate_id>` and record the override + rationale in the log.
   WARNs never block but must be surfaced verbatim.
4. **LIMIT by default.** MARKET only when the owner insists (the gate warns).
5. **Log every instruction** to `data/orders.jsonl` via `scripts/order_log.py`
   — creation, and later status changes (submitted/filled/cancelled).
6. **Refresh after fills** (the standard mcp_refresh flow) so the dashboard
   reflects the real book. `data/orders.jsonl` commits are data-only → may go
   straight to `master`.

## Place an order

1. **Live state** — call `get_account_summary` and `get_account_positions`
   (fresh MCP calls; don't size off stale JSON).
2. **Resolve the contract** — held names: `conid` is in `data/positions.json`.
   New names: `search_contracts`, pick the row whose `symbol` matches exactly,
   US primary listing, `sections` include STK; use its `underlying_contract_id`.
   For `create_order_instruction`, STK `contract_id_ex` is that id **as a string**.
3. **Live quote** — `get_price_snapshot` (`last`, `bid_ask`, `change`). Propose
   a limit near the touch (e.g. mid or last ± a few cents), not through it.
4. **Gate** — run and show the output:
   ```
   python3 scripts/trade_gate.py --ticker SGML --side BUY --qty 10 \
       --order-type LIMIT --limit 10.25 --last 10.46 --tif DAY
   ```
   Exit 1 (FAIL) → stop and present; proceed only on an explicit owner
   override of the named gate. Sizing rule of thumb: new positions ~2–3% NAV.
5. **Confirm with the owner — and capture the why.** Present the exact ticket
   + gate summary (notional, % NAV, position before→after, book gross after)
   and ask explicitly (AskUserQuestion when available). Anything other than a
   clear yes = no. Every order carries a **reason**: take it from the owner's
   message, or from the triggering recommendation/rebalance row (confirm it
   with the owner), or ask for one — never log an empty reason.
6. **Create the instruction** —
   `create_order_instruction(contract_id_ex="<conid>", side, quantity,
   order_type, limit_price, time_in_force)`. Show the returned **URL**
   prominently: the owner opens it in IBKR to review and **Submit**.
7. **Record** —
   ```
   python3 scripts/order_log.py --append --ticker SGML --side BUY --qty 10 \
       --order-type LIMIT --limit 10.25 --tif DAY --conid 511477158 \
       --instruction-id <id> --url <url> \
       --trigger-source owner|recommendation|rebalance|alert \
       --trigger-ref "<compact snapshot of the triggering row>" \
       --reason "<the owner's why, verbatim>" \
       --gates "size_order:PASS,..." --note "<operational context, overrides>"
   ```
   The dashboard's Orders tab renders trigger + reason — it is the
   execution-side mirror of the decision log. Commit `data/orders.jsonl` to
   `master` (data-only), message like `data: order log — BUY 10 SGML
   (instruction <id>)`.
8. **Follow through** — `get_order_instructions` shows it pending; after the
   owner submits: `get_account_orders` (live/filled) →
   `order_log.py --set-status --instruction-id <id> --status submitted|filled
   --fill-price <actual execution price from get_account_trades>`.
   Fills: `get_account_trades` (TODAY) — record the real fill price (and note a
   deviating order type/qty): it anchors the Orders tab's look-back Outcome
   column (`order_log.py --update-outcomes`, run by the fetch Action). After a
   fill, run the standard IBKR refresh (`scripts/mcp_refresh.py` flow) and
   commit so NAV/positions update; the daily Journal routine picks up the
   round-trip analytics.

## Trading from a recommendation or the Rebalance plan

When the owner says "execute the recommendation on X" / «בצע את ההמלצה על X»
or "do the rebalance row on Y" / «תבצע את שורת הריבאלנס של Y», the trigger is
documentable — capture it:

1. Look the row up **fresh**: recommendations in `data/micro.json`
   (`recommendations[]`: action/urgency/rationale; `tradeList[]`: side/qty/why)
   or the plan row in `data/rebalance.json` (`rows[]`: callTag/callText/target/
   dollar/verdict). Show it to the owner; the row suggests, the owner decides
   the final side/qty.
2. Run the normal flow above (live state → quote → gate → confirm). The gate
   and confirmation are NEVER skipped because a row "already says so".
3. Log with the linkage: `--trigger-source recommendation` (or `rebalance`),
   `--trigger-ref` = a compact snapshot (e.g. `"COVER, urgency high — thesis
   conflict with bullish steel"` or `"HALVE → target $23 (row 1)"`), and
   `--reason` = the rationale the owner confirmed (default: the row's own
   rationale/why text, edited as the owner wishes).
4. An alert-driven trade (pre-earnings de-risk from the Overview banner) uses
   `--trigger-source alert` the same way.

Owner-initiated trades with no source row default to `--trigger-source owner`
— the reason is still required.

The dashboard's Rebalance / Recommendations / Trade-List rows carry a ▶
button that deep-links into a new Claude Code session on this repo with
exactly such a command pre-filled in English (`/trade TICKER — from Rebalance
row N…` / `execute the recommendation…`, the row's rationale as the reason
seed). A session opened that way runs the matching flow above: look the row up
fresh, let the owner adjust side/qty/reason, and never skip the gate or the
confirmation.

## Cancel / status

- **Cancel**: `get_order_instructions` → find the id → confirm with the owner
  → `delete_order_instruction(id)` → `order_log.py --set-status ... cancelled`.
  (Already-submitted live orders are managed in the IBKR app, not the MCP.)
- **Status**: `get_order_instructions` (pending instructions),
  `get_account_orders` (live orders), `get_account_trades` (fills),
  `python3 scripts/order_log.py --list` (audit trail). Reconcile and update
  statuses that changed.

## Examples

- «קנה 10 מניות SGML בלימיט 10.20» → full flow above (trigger: owner; ask for
  the reason if not given).
- «בצע את ההמלצה על NUE» → look up the COVER recommendation in micro.json,
  present it, run the flow; log with trigger-source recommendation + its
  rationale as the default reason.
- «תבצע את שורה 1 מהריבאלנס» → same, from rebalance.json rows (trigger-source
  rebalance, ref e.g. "HALVE → target $23").
- «תכסה חצי מהשורט ב‑CLF» → qty = ceil(shares/2), side BUY (reduces short —
  gate treats it as de-risking), same flow.
- «שים שורט על FCX, 2% מהתיק» → size from live NAV, off-universe/known-name
  and bias gates will speak up; confirm, create, log.
- «בטל את ההוראה על SGML» / «מה קורה עם ההוראות שלי?» → cancel/status flows.
