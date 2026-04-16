#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DATABASE_DIR="$APP_ROOT/database"

OUTPUT_PATH="${1:-$APP_ROOT/out/coldpool_database.sqlite}"

mkdir -p "$(dirname "$OUTPUT_PATH")"
rm -f "$OUTPUT_PATH"

echo "=== CREATE SQLITE DATABASE ==="
sqlite3 "$OUTPUT_PATH" < "$DATABASE_DIR/artifacts.sql"
sqlite3 "$OUTPUT_PATH" < "$DATABASE_DIR/artifact_versions.sql"
sqlite3 "$OUTPUT_PATH" < "$DATABASE_DIR/disks.sql"
sqlite3 "$OUTPUT_PATH" < "$DATABASE_DIR/copies.sql"

echo "[OK] SQLite database created at: $OUTPUT_PATH"