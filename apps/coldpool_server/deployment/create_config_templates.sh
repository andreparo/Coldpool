#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

OUTPUT_DIR="${1:-$APP_ROOT/out/config}"

mkdir -p "$OUTPUT_DIR"

echo "=== CREATE CONFIG TEMPLATES ==="

cat > "$OUTPUT_DIR/coldpool.env.example" <<'EOF'
COLDPOOL_HOST=0.0.0.0
COLDPOOL_PORT=5000
COLDPOOL_FLASK_DEBUG=0
COLDPOOL_INSTALL_ROOT=/opt/coldpool
COLDPOOL_DATA_ROOT=/var/lib/coldpool
COLDPOOL_CONFIG_ROOT=/etc/coldpool
COLDPOOL_LOG_ROOT=/var/log/coldpool
COLDPOOL_DATABASE_PATH=/var/lib/coldpool/coldpool_database.sqlite
COLDPOOL_FRONTEND_DIST_PATH=/opt/coldpool/frontend/dist
EOF

cat > "$OUTPUT_DIR/coldpool.toml.example" <<'EOF'
[server]
host = "0.0.0.0"
port = 5000
debug = false

[paths]
database_path = "/var/lib/coldpool/coldpool_database.sqlite"
frontend_dist_path = "/opt/coldpool/frontend/dist"
log_root = "/var/log/coldpool"
EOF

echo "[OK] Config templates created in: $OUTPUT_DIR"