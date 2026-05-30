#!/bin/bash
# install.sh - installs env-watcher on Linux/Mac via systemd user service
set -e

BUS_DIR="$(dirname "$(realpath "$0")")"
PYTHON="${PYTHON:-python3}"

echo "[install] Installing dependencies..."
$PYTHON -m pip install mcp watchdog --quiet

echo "[install] Creating systemd user service..."
SERVICE_FILE="$HOME/.config/systemd/user/env-watcher.service"
mkdir -p "$(dirname $SERVICE_FILE)"
cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Antigravity env-watcher (agent-bus notifier)
After=network.target

[Service]
ExecStart=$PYTHON $BUS_DIR/watcher.py --daemon
Restart=always
RestartSec=5
Environment=AGENT_BUS_DB=$BUS_DIR/agentbus.db

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable env-watcher
systemctl --user start env-watcher
echo "[install] Done. env-watcher is active via systemd."
