#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

python3 -m black --check --line-length 135 apps/coldpool_server/src

npx prettier --check \
    apps/coldpool_web_app/src \
    apps/coldpool_web_app/index.html \
    apps/coldpool_web_app/package.json \
    apps/coldpool_web_app/tsconfig.json \
    apps/coldpool_web_app/tsconfig.app.json \
    apps/coldpool_web_app/tsconfig.node.json \
    apps/coldpool_web_app/vite.config.ts \
    apps/coldpool_web_app/eslint.config.js