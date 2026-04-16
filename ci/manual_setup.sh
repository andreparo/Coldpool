#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

runtime_image="${RUNTIME_IMAGE:?RUNTIME_IMAGE environment variable is required}"
build_number="${BUILD_NUMBER:?BUILD_NUMBER environment variable is required}"
manual_port="${COLDPOOL_MANUAL_PORT:-18180}"
manual_host="${COLDPOOL_MANUAL_HOST:-sunflower-power}"

container_name="coldpool-runtime-manual-${build_number}"

cleanup_on_failure() {
    docker rm -f "$container_name" >/dev/null 2>&1 || true
}

echo "=== START MANUAL CONTAINER ==="
docker rm -f "$container_name" >/dev/null 2>&1 || true

docker run -d \
    --name "$container_name" \
    -p "${manual_port}:5000" \
    "$runtime_image"

echo "=== WAIT FOR MANUAL CONTAINER HEALTH ==="
for _ in $(seq 1 30); do
    if curl --fail --silent "http://127.0.0.1:${manual_port}/api/health" >/dev/null; then
        cat > ci_manual.env <<EOF
MANUAL_CONTAINER_NAME=$container_name
MANUAL_PORT=$manual_port
MANUAL_HOST=$manual_host
MANUAL_URL=http://${manual_host}:${manual_port}
EOF
        echo "[OK] Manual container is ready at http://${manual_host}:${manual_port}"
        exit 0
    fi
    sleep 1
done

echo "[ERROR] Manual container did not become healthy in time." >&2
echo "=== CONTAINER STATUS ==="
docker ps -a --filter "name=${container_name}" || true

echo "=== CONTAINER INSPECT STATE ==="
docker inspect "$container_name" --format 'Status={{.State.Status}} Running={{.State.Running}} ExitCode={{.State.ExitCode}} Error={{.State.Error}}' || true

echo "=== CONTAINER LOGS ==="
docker logs "$container_name" || true

cleanup_on_failure
exit 1