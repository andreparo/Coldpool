#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

python3 ci/structure/check_readme.py .
python3 ci/structure/check_license.py .
python3 ci/structure/check_top_level_dirs.py .