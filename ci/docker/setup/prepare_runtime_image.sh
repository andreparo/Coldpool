#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$repo_root"

runtime_image="${1:?Usage: bash ci/docker/setup/prepare_runtime_image.sh <runtime_image> <package_tarball_relative_path>}"
package_tarball_relative_path="${2:?Usage: bash ci/docker/setup/prepare_runtime_image.sh <runtime_image> <package_tarball_relative_path>}"

if [[ ! -f "$repo_root/$package_tarball_relative_path" ]]; then
    echo "[ERROR] Package tarball not found: $repo_root/$package_tarball_relative_path" >&2
    exit 1
fi

docker build \
    --pull \
    --build-arg PACKAGE_TARBALL_RELATIVE_PATH="$package_tarball_relative_path" \
    -t "$runtime_image" \
    -f ci/docker/runtime-image/Dockerfile \
    .