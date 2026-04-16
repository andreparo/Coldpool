#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

VERSION="${1:?Usage: bash ci/build/package_release.sh <version> <arch_label>}"
ARCH_LABEL="${2:-linux-x86_64}"

PACKAGE_NAME="coldpool-${VERSION}-${ARCH_LABEL}"
WORK_DIR="$REPO_ROOT/apps/coldpool_server/out/package_work"
PACKAGE_ROOT="$WORK_DIR/$PACKAGE_NAME"
DIST_DIR="$REPO_ROOT/apps/coldpool_server/dist"

FRONTEND_APP_ROOT="$REPO_ROOT/apps/coldpool_web_app"
BACKEND_APP_ROOT="$REPO_ROOT/apps/coldpool_server"

rm -rf "$WORK_DIR"
mkdir -p "$PACKAGE_ROOT"
mkdir -p "$DIST_DIR"

echo "=== PACKAGE RELEASE ==="

bash "$FRONTEND_APP_ROOT/deployment/build_frontend.sh"
bash "$BACKEND_APP_ROOT/deployment/build_backend_wheel.sh"
bash "$BACKEND_APP_ROOT/deployment/create_sqlite_database.sh" \
    "$BACKEND_APP_ROOT/out/coldpool_database.sqlite"
bash "$BACKEND_APP_ROOT/deployment/create_config_templates.sh" \
    "$BACKEND_APP_ROOT/out/config"

mkdir -p "$PACKAGE_ROOT/backend"
mkdir -p "$PACKAGE_ROOT/frontend"
mkdir -p "$PACKAGE_ROOT/database"
mkdir -p "$PACKAGE_ROOT/config"
mkdir -p "$PACKAGE_ROOT/systemd"

cp "$REPO_ROOT/LICENSE" "$PACKAGE_ROOT/LICENSE"
printf '%s\n' "$VERSION" > "$PACKAGE_ROOT/VERSION"

cp "$BACKEND_APP_ROOT/deployment/install.sh" "$PACKAGE_ROOT/install.sh"
cp "$BACKEND_APP_ROOT/deployment/run.sh" "$PACKAGE_ROOT/run.sh"

cp "$BACKEND_APP_ROOT"/dist/*.whl "$PACKAGE_ROOT/backend/"
cp -R "$FRONTEND_APP_ROOT/dist" "$PACKAGE_ROOT/frontend/dist"
cp "$BACKEND_APP_ROOT/out/coldpool_database.sqlite" "$PACKAGE_ROOT/database/"
cp "$BACKEND_APP_ROOT/out/config/"* "$PACKAGE_ROOT/config/"
cp "$BACKEND_APP_ROOT/deployment/systemd/coldpool.service" "$PACKAGE_ROOT/systemd/"

chmod +x "$PACKAGE_ROOT/install.sh"
chmod +x "$PACKAGE_ROOT/run.sh"

tar -C "$WORK_DIR" -czf "$DIST_DIR/${PACKAGE_NAME}.tar.gz" "$PACKAGE_NAME"

echo "[OK] Release package created:"
echo "  $DIST_DIR/${PACKAGE_NAME}.tar.gz"