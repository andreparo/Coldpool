#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$repo_root"

echo "=== PYTHON TYPE CHECK WITH MYPY ==="

TARGETS=(
    apps/coldpool_server/src
)

if mypy "${TARGETS[@]}"; then
    echo "[OK] Mypy check passed."
else
    echo
    echo "[FAIL] Mypy check failed."
    echo "Mypy uses the top-level mypy.ini file."
    exit 1
fi