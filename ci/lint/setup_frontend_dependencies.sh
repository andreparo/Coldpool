#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$repo_root/apps/coldpool_web_app"

echo "=== FRONTEND DEPENDENCY SETUP ==="
npm ci
echo "[OK] Frontend dependencies installed."