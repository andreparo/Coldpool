#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

build_number="${BUILD_NUMBER:?BUILD_NUMBER environment variable is required}"
short_sha="${SHORT_SHA:?SHORT_SHA environment variable is required}"

package_tarball_relative_path="$(find apps/coldpool_server/dist -maxdepth 1 -type f -name 'coldpool-*.tar.gz' | sort | tail -n 1)"

if [[ -z "$package_tarball_relative_path" ]]; then
    echo "[ERROR] No package tarball found in apps/coldpool_server/dist." >&2
    exit 1
fi

runtime_image="coldpool-runtime:${build_number}-${short_sha}"

echo "=== BUILD RUNTIME IMAGE ==="
bash ci/docker/setup/prepare_runtime_image.sh "$runtime_image" "$package_tarball_relative_path"

cat > ci_runtime.env <<EOF
RUNTIME_IMAGE=$runtime_image
PACKAGE_TARBALL_RELATIVE_PATH=$package_tarball_relative_path
EOF

echo "[OK] Runtime image created: $runtime_image"