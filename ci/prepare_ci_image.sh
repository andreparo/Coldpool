#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

image_tag="${1:?Usage: bash ci/prepare_ci_image.sh <image_tag>}"

docker build \
    -t "$image_tag" \
    -f ci/docker/project-ci/Dockerfile \
    .