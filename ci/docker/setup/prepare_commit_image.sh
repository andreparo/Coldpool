#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$repo_root"

dependency_image="${1:?Usage: bash ci/docker/setup/prepare_commit_image.sh <dependency_image> <commit_image>}"
commit_image="${2:?Usage: bash ci/docker/setup/prepare_commit_image.sh <dependency_image> <commit_image>}"

docker build \
    --pull=false \
    --build-arg BASE_IMAGE="$dependency_image" \
    -t "$commit_image" \
    -f ci/docker/commit-image/Dockerfile \
    .