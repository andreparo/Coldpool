#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$repo_root/apps/coldpool_web_app"

echo "=== FRONTEND TYPE CHECK WITH TSC ==="

tsc_args=(
    --noEmit
    -p tsconfig.app.json
)

if [[ -n "${TSC_BUILDINFO_FILE:-}" ]]; then
    tsc_args+=(--incremental --tsBuildInfoFile "$TSC_BUILDINFO_FILE")
fi

if npx tsc "${tsc_args[@]}"; then
    echo "[OK] TypeScript check passed."
else
    echo
    echo "[FAIL] TypeScript check failed."
    exit 1
fi