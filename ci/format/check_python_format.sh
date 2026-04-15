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
    echo "To fix it, run:"
    echo "docker run --rm -v \"$PWD\":/workspace -w /workspace coldpool-ci-base:1 black --line-length 135 apps/coldpool_server/src"
    exit 1
fi