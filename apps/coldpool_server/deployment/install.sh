#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_ROOT="$SCRIPT_DIR"

DEFAULT_INSTALL_ROOT="/opt/coldpool"
DEFAULT_PORT="5000"
DEFAULT_DATA_ROOT="/var/lib/coldpool"
DEFAULT_CONFIG_ROOT="/etc/coldpool"
DEFAULT_LOG_ROOT="/var/log/coldpool"

NONINTERACTIVE="${COLDPOOL_NONINTERACTIVE:-0}"
INSTALL_ROOT="${COLDPOOL_INSTALL_ROOT:-$DEFAULT_INSTALL_ROOT}"
DATA_ROOT="${COLDPOOL_DATA_ROOT:-$DEFAULT_DATA_ROOT}"
CONFIG_ROOT="${COLDPOOL_CONFIG_ROOT:-$DEFAULT_CONFIG_ROOT}"
LOG_ROOT="${COLDPOOL_LOG_ROOT:-$DEFAULT_LOG_ROOT}"
PORT="${COLDPOOL_PORT:-$DEFAULT_PORT}"

print_header() {
    echo
    echo "============================================================"
    echo " Coldpool installer"
    echo "============================================================"
    echo
}

require_command() {
    local command_name="$1"
    if ! command -v "$command_name" >/dev/null 2>&1; then
        echo "[ERROR] Required command not found: $command_name" >&2
        exit 1
    fi
}

ask_value() {
    local prompt="$1"
    local current_value="$2"
    local output_var_name="$3"

    if [[ "$NONINTERACTIVE" == "1" ]]; then
        printf -v "$output_var_name" '%s' "$current_value"
        return
    fi

    local user_value
    read -r -p "$prompt [$current_value]: " user_value
    if [[ -z "$user_value" ]]; then
        printf -v "$output_var_name" '%s' "$current_value"
    else
        printf -v "$output_var_name" '%s' "$user_value"
    fi
}

ensure_directories() {
    echo "[INFO] Creating directories..."
    sudo mkdir -p "$INSTALL_ROOT"
    sudo mkdir -p "$DATA_ROOT"
    sudo mkdir -p "$CONFIG_ROOT"
    sudo mkdir -p "$LOG_ROOT"
}

copy_package_files() {
    echo "[INFO] Copying packaged files..."

    sudo mkdir -p "$INSTALL_ROOT/backend"
    sudo mkdir -p "$INSTALL_ROOT/frontend"
    sudo mkdir -p "$INSTALL_ROOT/systemd"
    sudo mkdir -p "$INSTALL_ROOT/bin"

    sudo cp -f "$PACKAGE_ROOT/VERSION" "$INSTALL_ROOT/VERSION"
    sudo cp -f "$PACKAGE_ROOT/LICENSE" "$INSTALL_ROOT/LICENSE"
    sudo cp -f "$PACKAGE_ROOT/run.sh" "$INSTALL_ROOT/run.sh"

    if [[ -d "$PACKAGE_ROOT/backend" ]]; then
        sudo cp -f "$PACKAGE_ROOT"/backend/* "$INSTALL_ROOT/backend/"
    fi

    if [[ -d "$PACKAGE_ROOT/frontend" ]]; then
        sudo rm -rf "$INSTALL_ROOT/frontend/dist"
        sudo mkdir -p "$INSTALL_ROOT/frontend"
        sudo cp -R "$PACKAGE_ROOT/frontend/dist" "$INSTALL_ROOT/frontend/dist"
    fi

    if [[ -d "$PACKAGE_ROOT/systemd" ]]; then
        sudo cp -f "$PACKAGE_ROOT"/systemd/* "$INSTALL_ROOT/systemd/" || true
    fi

    sudo chmod +x "$INSTALL_ROOT/run.sh"
}

install_python_backend() {
    echo "[INFO] Installing backend wheel..."

    local wheel_path
    wheel_path="$(find "$INSTALL_ROOT/backend" -maxdepth 1 -type f -name '*.whl' | head -n 1 || true)"

    if [[ -z "$wheel_path" ]]; then
        echo "[ERROR] No backend wheel found in $INSTALL_ROOT/backend" >&2
        exit 1
    fi

    require_command python3
    require_command pip3

    sudo python3 -m pip install --upgrade pip
    sudo python3 -m pip install "$wheel_path"
}

initialize_database() {
    echo "[INFO] Initializing database..."

    if [[ ! -f "$DATA_ROOT/coldpool_database.sqlite" ]]; then
        sudo cp -f "$PACKAGE_ROOT/database/coldpool_database.sqlite" "$DATA_ROOT/coldpool_database.sqlite"
    fi

    sudo chmod 664 "$DATA_ROOT/coldpool_database.sqlite" || true
}

initialize_config() {
    echo "[INFO] Initializing config..."

    if [[ ! -f "$CONFIG_ROOT/coldpool.env" ]]; then
        sudo cp -f "$PACKAGE_ROOT/config/coldpool.env.example" "$CONFIG_ROOT/coldpool.env"
    fi

    if [[ ! -f "$CONFIG_ROOT/coldpool.toml" ]]; then
        sudo cp -f "$PACKAGE_ROOT/config/coldpool.toml.example" "$CONFIG_ROOT/coldpool.toml"
    fi

    sudo sed -i "s|^COLDPOOL_PORT=.*$|COLDPOOL_PORT=$PORT|g" "$CONFIG_ROOT/coldpool.env"
    sudo sed -i "s|^COLDPOOL_INSTALL_ROOT=.*$|COLDPOOL_INSTALL_ROOT=$INSTALL_ROOT|g" "$CONFIG_ROOT/coldpool.env"
    sudo sed -i "s|^COLDPOOL_DATA_ROOT=.*$|COLDPOOL_DATA_ROOT=$DATA_ROOT|g" "$CONFIG_ROOT/coldpool.env"
    sudo sed -i "s|^COLDPOOL_CONFIG_ROOT=.*$|COLDPOOL_CONFIG_ROOT=$CONFIG_ROOT|g" "$CONFIG_ROOT/coldpool.env"
    sudo sed -i "s|^COLDPOOL_LOG_ROOT=.*$|COLDPOOL_LOG_ROOT=$LOG_ROOT|g" "$CONFIG_ROOT/coldpool.env"
}

install_systemd_service() {
    local service_template="$INSTALL_ROOT/systemd/coldpool.service"

    if [[ ! -f "$service_template" ]]; then
        echo "[WARN] No systemd service template found. Skipping service installation."
        return
    fi

    echo "[INFO] Installing systemd service..."

    local temp_service
    temp_service="$(mktemp)"
    cp "$service_template" "$temp_service"

    sed -i "s|__COLDPOOL_INSTALL_ROOT__|$INSTALL_ROOT|g" "$temp_service"
    sed -i "s|__COLDPOOL_CONFIG_ROOT__|$CONFIG_ROOT|g" "$temp_service"
    sed -i "s|__COLDPOOL_DATA_ROOT__|$DATA_ROOT|g" "$temp_service"
    sed -i "s|__COLDPOOL_LOG_ROOT__|$LOG_ROOT|g" "$temp_service"

    sudo cp -f "$temp_service" /etc/systemd/system/coldpool.service
    rm -f "$temp_service"

    sudo systemctl daemon-reload
}

print_summary() {
    echo
    echo "[OK] Coldpool installation completed."
    echo
    echo "Install root : $INSTALL_ROOT"
    echo "Data root    : $DATA_ROOT"
    echo "Config root  : $CONFIG_ROOT"
    echo "Log root     : $LOG_ROOT"
    echo "Port         : $PORT"
    echo
    echo "Run manually with:"
    echo "  sudo $INSTALL_ROOT/run.sh"
    echo
    echo "If systemd service was installed:"
    echo "  sudo systemctl start coldpool"
    echo "  sudo systemctl status coldpool"
    echo
}

main() {
    print_header

    require_command sudo
    require_command sed
    require_command cp

    ask_value "Install root" "$INSTALL_ROOT" INSTALL_ROOT
    ask_value "Data root" "$DATA_ROOT" DATA_ROOT
    ask_value "Config root" "$CONFIG_ROOT" CONFIG_ROOT
    ask_value "Log root" "$LOG_ROOT" LOG_ROOT
    ask_value "Flask port" "$PORT" PORT

    ensure_directories
    copy_package_files
    install_python_backend
    initialize_database
    initialize_config
    install_systemd_service
    print_summary
}

main "$@"