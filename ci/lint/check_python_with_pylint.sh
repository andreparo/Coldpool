#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$repo_root"

echo "=== PYTHON LINT CHECK WITH PYLINT ==="

TARGETS=(
    apps/coldpool_server/src
)

if pylint "${TARGETS[@]}"; then
    echo "[OK] Pylint check passed."
else
    echo
    echo "[FAIL] Pylint check failed."
    echo "Pylint uses the top-level .pylintrc file."
    exit 1
fi