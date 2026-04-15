#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

python3 -m pip install black==25.11.0
python3 -m black --check --line-length 135 apps/coldpool_server/src

cd apps/coldpool_web_app
npm install
npx prettier --check \
    src \
    index.html \
    package.json \
    tsconfig.json \
    tsconfig.app.json \
    tsconfig.node.json \
    vite.config.ts \
    eslint.config.js