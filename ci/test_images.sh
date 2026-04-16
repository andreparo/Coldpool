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
container_name="coldpool-runtime-smoke-${build_number}"
host_port="15000"

cleanup() {
    docker rm -f "$container_name" >/dev/null 2>&1 || true
}
trap cleanup EXIT

echo "=== BUILD RUNTIME IMAGE ==="
bash ci/docker/setup/prepare_runtime_image.sh "$runtime_image" "$package_tarball_relative_path"

echo "=== START RUNTIME CONTAINER ==="
docker rm -f "$container_name" >/dev/null 2>&1 || true
docker run -d \
    --name "$container_name" \
    -p "${host_port}:5000" \
    "$runtime_image"

echo "=== WAIT FOR /api/health ==="
for _ in $(seq 1 30); do
    if curl --fail --silent "http://127.0.0.1:${host_port}/api/health" >/dev/null; then
        echo "[OK] Runtime image is healthy."
        exit 0
    fi
    sleep 1
done

echo "[ERROR] Runtime image did not become healthy in time." >&2
echo "=== CONTAINER STATUS ==="
docker ps -a --filter "name=${container_name}" || true

echo "=== CONTAINER INSPECT STATE ==="
docker inspect "$container_name" --format 'Status={{.State.Status}} Running={{.State.Running}} ExitCode={{.State.ExitCode}} Error={{.State.Error}}' || true

echo "=== CONTAINER LOGS ==="
docker logs "$container_name" || true

echo "=== PROCESS LIST INSIDE CONTAINER ==="
docker exec "$container_name" ps aux || true

echo "=== LISTENING PORTS INSIDE CONTAINER ==="
docker exec "$container_name" bash -lc 'command -v ss >/dev/null 2>&1 && ss -ltnp || netstat -ltnp || true' || true

echo "=== TRY HEALTH FROM INSIDE CONTAINER ==="
docker exec "$container_name" bash -lc 'curl -v --fail http://127.0.0.1:5000/api/health' || true

exit 1