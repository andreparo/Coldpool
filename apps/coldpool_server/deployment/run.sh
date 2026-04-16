#!/usr/bin/env bash
set -euo pipefail

INSTALL_ROOT="${COLDPOOL_INSTALL_ROOT:-/opt/coldpool}"
CONFIG_ROOT="${COLDPOOL_CONFIG_ROOT:-/etc/coldpool}"
DATA_ROOT="${COLDPOOL_DATA_ROOT:-/var/lib/coldpool}"
LOG_ROOT="${COLDPOOL_LOG_ROOT:-/var/log/coldpool}"

ENV_FILE="$CONFIG_ROOT/coldpool.env"

if [[ -f "$ENV_FILE" ]]; then
    # shellcheck disable=SC1090
    source "$ENV_FILE"
fi

HOST="${COLDPOOL_HOST:-0.0.0.0}"
PORT="${COLDPOOL_PORT:-5000}"
FLASK_DEBUG="${COLDPOOL_FLASK_DEBUG:-0}"
DATABASE_PATH="${COLDPOOL_DATABASE_PATH:-$DATA_ROOT/coldpool_database.sqlite}"
FRONTEND_DIST_PATH="${COLDPOOL_FRONTEND_DIST_PATH:-$INSTALL_ROOT/frontend/dist}"

export COLDPOOL_DATABASE_PATH="$DATABASE_PATH"
export COLDPOOL_FRONTEND_DIST_PATH="$FRONTEND_DIST_PATH"

mkdir -p "$LOG_ROOT"

exec python3 -m coldpool_server