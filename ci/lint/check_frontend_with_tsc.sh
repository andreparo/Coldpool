#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$repo_root/apps/coldpool_web_app"

echo "=== FRONTEND TYPE CHECK WITH TSC ==="

npm ci

if npx tsc --noEmit -p tsconfig.app.json; then
    echo "[OK] TypeScript check passed."
else
    echo
    echo "[FAIL] TypeScript check failed."
    exit 1
fi