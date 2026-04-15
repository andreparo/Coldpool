#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

bash ci/lint/check_python_with_pylint.sh
bash ci/lint/check_python_with_mypy.sh
bash ci/lint/setup_frontend_dependencies.sh
bash ci/lint/check_frontend_with_eslint.sh
bash ci/lint/check_frontend_with_tsc.sh