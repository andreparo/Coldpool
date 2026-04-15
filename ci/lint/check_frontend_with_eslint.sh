#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$repo_root/apps/coldpool_web_app"

echo "=== FRONTEND LINT CHECK WITH ESLINT ==="

npm ci

if npx eslint src vite.config.ts eslint.config.js; then
    echo "[OK] ESLint check passed."
else
    echo
    echo "[FAIL] ESLint check failed."
    exit 1
fi