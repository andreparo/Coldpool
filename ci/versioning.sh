#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

git config --global --add safe.directory "$repo_root"

python3 ci/versioning/verify_changelog.py
python3 ci/versioning/compute_version.py > ci_version.env
cat ci_version.env