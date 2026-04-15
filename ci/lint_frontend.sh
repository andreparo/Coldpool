#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$repo_root"

bash ci/lint/check_frontend_with_eslint.sh
bash ci/lint/check_frontend_with_tsc.sh