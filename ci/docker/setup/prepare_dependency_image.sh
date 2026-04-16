#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$repo_root"

dependency_image="${1:?Usage: bash ci/docker/setup/prepare_dependency_image.sh <dependency_image>}"

docker build \
    --pull \
    -t "$dependency_image" \
    -f ci/docker/dependency-image/Dockerfile \
    .