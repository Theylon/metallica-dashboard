#!/usr/bin/env bash
# Local standards gate — run before you open a PR.
#
# This is the same set of checks CI runs (.github/workflows/standards.yml), so
# "green here" means "green there". It is intentionally dependency-free: only
# python3 and git, both already required to work on this repo.
#
#   ./scripts/check.sh
#
# Exit 0 = all checks pass. Non-zero = something a reviewer would bounce.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 2

fail=0
step() { printf '\n\033[1m▶ %s\033[0m\n' "$1"; }

# 1) Python syntax — every script must at least compile.
step "Compiling Python scripts"
if python3 -m py_compile scripts/*.py; then
  echo "  ok: all scripts compile"
else
  echo "  ERR: a script failed to compile"; fail=1
fi

# 2) Data contract — the dashboard's fetched JSON must hold its shape.
step "Validating data/ contract"
python3 scripts/validate_data.py || fail=1

# 3) Secret guard — never commit private keys, key files, or a real .env. The
#    password gate in index.html is a client-side hash (fine to commit), but the
#    IBKR OAuth private key + account id are secrets and live only in GitHub
#    Actions secrets. The PEM marker is anchored to line-start so it catches a
#    pasted key block / key file but not docs that mention the format inline.
step "Scanning tracked files for secrets"
secret_hits=$(git grep -nI -E '^-{5}BEGIN [A-Z ]*PRIVATE KEY-{5}' 2>/dev/null || true)
keyfiles=$(git ls-files -- '*.pem' '*.key' 'id_rsa' 'id_rsa*' '*.env' '.env' 2>/dev/null || true)
if [ -n "$secret_hits" ] || [ -n "$keyfiles" ]; then
  echo "  ERR: possible secret committed:"
  [ -n "$secret_hits" ] && echo "$secret_hits" | sed 's/^/    /'
  [ -n "$keyfiles" ] && echo "    key/env file(s) tracked:" && echo "$keyfiles" | sed 's/^/      /'
  fail=1
else
  echo "  ok: no private keys, key files, or .env files tracked"
fi

# 4) Optional lint — advisory only, never blocks. Runs if ruff is installed.
step "Lint (advisory)"
if command -v ruff >/dev/null 2>&1; then
  ruff check scripts/ || echo "  (ruff findings above are advisory, not blocking)"
else
  echo "  skip: ruff not installed (pip install ruff to enable)"
fi

echo
if [ "$fail" -eq 0 ]; then
  echo -e "\033[32m✓ all standards checks passed\033[0m"
else
  echo -e "\033[31m✗ standards checks failed — fix the ERR lines above\033[0m"
fi
exit "$fail"
