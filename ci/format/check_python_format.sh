#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$repo_root"

echo "=== PYTHON FORMAT CHECK ==="

if black --check --diff --line-length 135 apps/coldpool_server/src; then
    echo "[OK] Python formatting is valid."
else
    echo
    echo "[FAIL] Python formatting is invalid."

    if [[ -n "${HOST_WORKSPACE:-}" ]]; then
        echo "To fix it on the Jenkins host, run:"
        echo "docker run --rm -v \"$HOST_WORKSPACE\":/workspace -w /workspace coldpool-ci-base:1 black --line-length 135 apps/coldpool_server/src"
    else
        echo "To fix it from the repository root, run:"
        echo "docker run --rm -v \"\$PWD\":/workspace -w /workspace coldpool-ci-base:1 black --line-length 135 apps/coldpool_server/src"
    fi

    exit 1
fi