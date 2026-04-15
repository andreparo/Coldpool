#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$repo_root/apps/coldpool_web_app"

echo "=== FRONTEND LINT CHECK WITH ESLINT ==="

eslint_args=(
    src
    vite.config.ts
    eslint.config.js
)

if [[ -n "${ESLINT_CACHE_FILE:-}" ]]; then
    eslint_args+=(--cache --cache-location "$ESLINT_CACHE_FILE")
fi

if npx eslint "${eslint_args[@]}"; then
    echo "[OK] ESLint check passed."
else
    echo
    echo "[FAIL] ESLint check failed."
    exit 1
fi