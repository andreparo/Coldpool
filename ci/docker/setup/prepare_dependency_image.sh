#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$repo_root"

dependency_image="${1:?Usage: bash ci/docker/setup/prepare_dependency_image.sh <dependency_image>}"

if docker image inspect "$dependency_image" >/dev/null 2>&1; then
    echo "Dependency image already exists: $dependency_image"
    exit 0
fi

docker build \
    -t "$dependency_image" \
    -f ci/docker/dependency-image/Dockerfile \
    .