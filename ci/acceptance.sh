#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

export PYTHONPATH="apps/coldpool_server/src:."
export COLDPOOL_ACCEPTANCE_BASE_URL="${COLDPOOL_ACCEPTANCE_BASE_URL:?COLDPOOL_ACCEPTANCE_BASE_URL environment variable is required}"

pytest tests/acceptance -v "$@"