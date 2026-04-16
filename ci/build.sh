#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

version="${VERSION:?VERSION environment variable is required}"
arch_label="${1:-linux-x86_64}"

bash "$repo_root/ci/build/package_release.sh" "$version" "$arch_label"