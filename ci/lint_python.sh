#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$repo_root"

bash ci/lint/check_python_with_pylint.sh
bash ci/lint/check_python_with_mypy.sh