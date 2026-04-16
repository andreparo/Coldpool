#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$APP_ROOT"

echo "=== BUILD BACKEND WHEEL ==="
python3 -m pip install --upgrade pip build
python3 -m build --wheel

if ! find "$APP_ROOT/dist" -maxdepth 1 -type f -name '*.whl' | grep -q .; then
    echo "[ERROR] No wheel found in dist/." >&2
    exit 1
fi

echo "[OK] Backend wheel built successfully."