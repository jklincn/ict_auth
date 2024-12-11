#!/usr/bin/env bash

# This is just a helper script to install SakuraFrp frpc client.

set -e

FRPC_PATH="$HOME/.local/bin/frpc"
FRPC_URL="https://nya.globalslb.net/natfrp/client/frpc/0.51.0-sakura-9.3/frpc_linux_amd64"
EXPECTED_MD5="23ee541dfb197cdd52f716542a89d204"

mkdir -p "$HOME/.local/bin"

cd "$HOME/.local/bin"

echo "[INFO] Downloading frpc..."
if [ -f "$FRPC_PATH" ]; then
    echo "[WARNING] $FRPC_PATH already exists, overwriting..."
fi
if ! curl -sSf -o frpc "$FRPC_URL"; then
    echo "[ERROR] Failed to download frpc client."
    exit 1
fi

chmod 755 frpc

DOWNLOADED_MD5=$(md5sum frpc | awk '{print $1}')
if [ "$DOWNLOADED_MD5" != "$EXPECTED_MD5" ]; then
    echo "[ERROR] MD5 check failed. Expected: $EXPECTED_MD5, Real: $DOWNLOADED_MD5"
    exit 1
fi

read -ep "[INFO] Input your frpc start parameter (example: -f sometoken:12345): " PARAMS < /dev/tty

USER="$USER"
GROUP=$(id -gn $USER)

SERVICE="[Unit]
Description=SakuraFrp Launcher
After=network.target

[Service]
Type=simple
User=$USER
Group=$GROUP
TimeoutStopSec=20
Restart=always
RestartSec=5s
ExecStart=$FRPC_PATH $PARAMS

[Install]
WantedBy=multi-user.target"

echo "$SERVICE" | sudo tee "/etc/systemd/system/frpc.service" > /dev/null

sudo systemctl daemon-reload
sudo systemctl start frpc.service
sudo systemctl enable frpc.service

echo "[INFO] Installation successful."