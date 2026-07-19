#!/bin/bash
# SessionStart hook — Metallica dashboard auto-refresh.
# The hook can't call MCP itself, so it injects a directive telling the agent
# to refresh the live IBKR data (via the connected IBKR MCP) at session start.
set -euo pipefail

# Only in Claude Code on the web, where the IBKR MCP is connected.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# Capture the hook's stdin (SessionStart JSON) BEFORE running python — python's
# own stdin below is the heredoc, so it reads the hook payload from this env var.
HOOK_INPUT="$(cat || true)"
export HOOK_INPUT

python3 <<'PY'
import json, os, sys

# Only auto-refresh on a real session open (not /clear or context compaction).
raw = os.environ.get("HOOK_INPUT", "")
try:
    src = json.loads(raw).get("source", "startup") if raw.strip() else "startup"
except Exception:
    src = "startup"
if src not in ("startup", "resume"):
    sys.exit(0)

directive = (
    "Metallica dashboard — AUTO-REFRESH (the owner opted in via this SessionStart hook).\n"
    "At the start of this session, if the Interactive_Brokers_IBKR MCP is connected, refresh the live data before other work:\n"
    "1) Call these IBKR MCP tools and save each raw JSON result verbatim to /tmp:\n"
    "   get_account_summary            -> /tmp/ibkr_summary.json\n"
    "   get_account_positions          -> /tmp/ibkr_positions.json\n"
    "   get_account_balances           -> /tmp/ibkr_balances.json\n"
    "   get_pa_performance_all_periods -> /tmp/ibkr_perf.json\n"
    "   Then pull benchmark price history so benchmarks.json stays current. For each ETF call\n"
    "   get_price_history (security_type=STK, step=ONE_DAY, period=THREE_MONTHS, outside_rth=false)\n"
    "   and save the raw JSON verbatim to /tmp/ibkr_bench_<TICKER>.json (conids from BENCH_CONIDS in mcp_refresh.py):\n"
    "   SPY  contract_id 756733    -> /tmp/ibkr_bench_SPY.json\n"
    "   XME  contract_id 45540699  -> /tmp/ibkr_bench_XME.json\n"
    "   SLV  contract_id 39039301  -> /tmp/ibkr_bench_SLV.json\n"
    "   CPER contract_id 97462781  -> /tmp/ibkr_bench_CPER.json\n"
    "2) Run: python3 scripts/mcp_refresh.py  (rewrites data/positions.json, account.json, pnl.json, "
    "and benchmarks.json; leaves report.json untouched).\n"
    "3) Commit the data/ change and get it onto master so GitHub Pages redeploys "
    "(push to master, or open a PR and merge — it is a data-only refresh).\n"
    "4) Briefly tell the user: refreshed NAV and daily P&L, with the live URL "
    "https://theylon.github.io/metallica-dashboard/ .\n"
    "If the IBKR MCP is unavailable, just say so and skip. Do not modify report.json unless asked."
)

print(json.dumps({"hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": directive,
}}))
PY
