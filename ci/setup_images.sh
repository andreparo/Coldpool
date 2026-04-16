#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

build_number="${1:?Usage: bash ci/setup_images.sh <build_number> <short_sha>}"
short_sha="${2:?Usage: bash ci/setup_images.sh <build_number> <short_sha>}"

base_image="coldpool-ci-base:1"
dependency_image="coldpool-ci-dependency:1"
commit_image="coldpool-ci-commit:${build_number}-${short_sha}"

bash ci/docker/setup/prepare_base_image.sh "$base_image"
bash ci/docker/setup/prepare_dependency_image.sh "$dependency_image"
bash ci/docker/setup/prepare_commit_image.sh "$dependency_image" "$commit_image"

cat > ci_images.env <<EOF
BASE_IMAGE=$base_image
DEPENDENCY_IMAGE=$dependency_image
COMMIT_IMAGE=$commit_image
EOF