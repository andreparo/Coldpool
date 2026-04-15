#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$repo_root"

echo "=== FRONTEND FORMAT CHECK ==="

PRETTIER_TARGETS=(
    apps/coldpool_web_app/src
    apps/coldpool_web_app/index.html
    apps/coldpool_web_app/package.json
    apps/coldpool_web_app/tsconfig.json
    apps/coldpool_web_app/tsconfig.app.json
    apps/coldpool_web_app/tsconfig.node.json
    apps/coldpool_web_app/vite.config.ts
    apps/coldpool_web_app/eslint.config.js
)

if prettier --check "${PRETTIER_TARGETS[@]}"; then
    echo "[OK] Frontend formatting is valid."
else
    echo
    echo "[FAIL] Frontend formatting is invalid."

    if [[ -n "${HOST_WORKSPACE:-}" ]]; then
        echo "To fix it on the Jenkins host, run:"
        echo "docker run --rm -v \"$HOST_WORKSPACE\":/workspace -w /workspace coldpool-ci-base:1 prettier --write ${PRETTIER_TARGETS[*]}"
    else
        echo "To fix it from the repository root, run:"
        echo "docker run --rm -v \"\$PWD\":/workspace -w /workspace coldpool-ci-base:1 prettier --write ${PRETTIER_TARGETS[*]}"
    fi

    exit 1
fi