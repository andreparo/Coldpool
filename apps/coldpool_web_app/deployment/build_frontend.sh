#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$APP_ROOT"

echo "=== BUILD FRONTEND ==="
npm ci
npm run build

if [[ ! -d "$APP_ROOT/dist" ]]; then
    echo "[ERROR] Frontend build did not create dist/." >&2
    exit 1
fi

echo "[OK] Frontend built successfully."