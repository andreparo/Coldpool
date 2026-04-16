#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

runtime_image="${RUNTIME_IMAGE:?RUNTIME_IMAGE environment variable is required}"
build_number="${BUILD_NUMBER:?BUILD_NUMBER environment variable is required}"

container_name="coldpool-runtime-smoke-${build_number}"
host_port="${COLDPOOL_SMOKE_PORT:-15000}"

cleanup() {
    docker rm -f "$container_name" >/dev/null 2>&1 || true
}
trap cleanup EXIT

echo "=== START SMOKE CONTAINER ==="
docker rm -f "$container_name" >/dev/null 2>&1 || true
docker run -d \
    --name "$container_name" \
    -p "${host_port}:5000" \
    "$runtime_image"

echo "=== WAIT FOR /api/health ==="
for _ in $(seq 1 30); do
    if curl --fail --silent "http://127.0.0.1:${host_port}/api/health" >/dev/null; then
        echo "[OK] Smoke check passed."
        exit 0
    fi
    sleep 1
done

echo "[ERROR] Smoke check failed: /api/health did not become ready." >&2
echo "=== CONTAINER STATUS ==="
docker ps -a --filter "name=${container_name}" || true

echo "=== CONTAINER INSPECT STATE ==="
docker inspect "$container_name" --format 'Status={{.State.Status}} Running={{.State.Running}} ExitCode={{.State.ExitCode}} Error={{.State.Error}}' || true

echo "=== CONTAINER LOGS ==="
docker logs "$container_name" || true

echo "=== PROCESS LIST INSIDE CONTAINER ==="
docker exec "$container_name" ps aux || true

echo "=== TRY HEALTH FROM INSIDE CONTAINER ==="
docker exec "$container_name" bash -lc 'curl -v --fail http://127.0.0.1:5000/api/health' || true

exit 1