#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$repo_root"

base_image="${1:?Usage: bash ci/docker/setup/prepare_base_image.sh <base_image>}"

docker build \
    --pull \
    -t "$base_image" \
    -f ci/docker/base-image/Dockerfile \
    .