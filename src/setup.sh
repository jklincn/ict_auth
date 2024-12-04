#!/usr/bin/env bash

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
INSTALL_DIR="$HOME/.local/ict_auth"
BIN_DIR="$HOME/.local/bin"
VENV_DIR="$INSTALL_DIR/venv"

if [ "$EUID" -eq 0 ]; then
    SUDO=""
else
    SUDO="sudo"
fi

function show_help() {
    echo "Usage:"
    echo "  ict_auth              Start Internet authentication"
    echo "  ict_auth --help       Show help message"
    echo "  ict_auth --enable     Enable and start the persistent connection service"
    echo "  ict_auth --disable    Disable the persistent connection service."
    echo "  ict_auth --log        View the logs for the persistent connection service."
    echo "  ict_auth --uninstall  Uninstall ict_auth from the system"
    echo "  ict_auth --version    Print version information"
}

# Install
if [ ! -d "$INSTALL_DIR" ]; then
    echo "[INFO] Installing..."

    mkdir -p "$INSTALL_DIR" "$BIN_DIR"
    cp -r "$SCRIPT_DIR"/* "$INSTALL_DIR/"
    ln -sf "$INSTALL_DIR/setup.sh" "$BIN_DIR/ict_auth"

    packages=(
        python3
        python3-pip
        python3-venv
        libnss3
        libgconf-2-4
        libx11-xcb1
        libxcomposite1
        libxcursor1
        libxdamage1
        libxi6
        libxtst6
        libatk1.0-0
        libcups2
        libxrandr2
        libasound2
        libpangocairo-1.0-0
        libxshmfence1
        libgbm1
        libxkbcommon0
        libatk-bridge2.0-0
    )

    missing_packages=()

    for pkg in "${packages[@]}"; do
        if ! dpkg -s "$pkg" >/dev/null 2>&1; then
            missing_packages+=("$pkg")
        fi
    done

    if [ ${#missing_packages[@]} -gt 0 ]; then
        echo "Missing packages: ${missing_packages[*]}"
        read -p "Do you want to install these packages? [Y/n] " choice
        choice=${choice:-y}
        if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
            echo "Updating package lists..."
            $SUDO apt-get update
            echo "Installing missing packages: ${missing_packages[*]}"
            $SUDO apt-get install -y "${missing_packages[@]}"
        else
            echo "Installation of missing packages aborted."
            exit 0
        fi
    fi

    /usr/bin/python3 -m venv "$VENV_DIR"

    source "$VENV_DIR/bin/activate"

    pip install --no-index --find-links="$SCRIPT_DIR/wheel" selenium

    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to install dependency."
        rm -f "$BIN_DIR/ict_auth"
        rm -rf "$INSTALL_DIR"
        exit 1
    fi

    if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
        echo -e "\e[33m[WARNING] $BIN_DIR is not in your PATH.\e[0m"
        echo "Run the following command to add it to your PATH temporarily:"
        echo "  export PATH=\"$BIN_DIR:\$PATH\""
    fi

    echo "[INFO] ict_auth successfully installed in $INSTALL_DIR"
    exit 0
fi


function service_enable() {
    if systemctl list-timers | grep -q "ict_auth.timer"; then
        echo "[INFO] Persistent connection service has been enabled."
    else
        echo "[INFO] Starting persistent connection service..."
        echo "============================="
        read -ep "ICT Username: " ICT_USERNAME
        read -esp "ICT Password: " ICT_PASSWORD
        echo
        echo "============================="

        echo "[INFO] Verifying account..."
        source "$VENV_DIR/bin/activate"
        ICT_USERNAME=$ICT_USERNAME ICT_PASSWORD=$ICT_PASSWORD python3 "$INSTALL_DIR/service.py" --check
        
        if [ $? -ne 0 ]; then
            exit 1
        fi    

        echo "ICT_USERNAME=$ICT_USERNAME" > "$INSTALL_DIR/.env"
        echo "ICT_PASSWORD=$ICT_PASSWORD" >> "$INSTALL_DIR/.env"
        chmod 600 "$INSTALL_DIR/.env"
        echo "============================="
        read -ep "Frpc Start Command (use absolute path!!): " FRPC_COMMAND
        echo "============================="

        VERSION=$(cat "$INSTALL_DIR/version.txt")
        USER="$USER"
        GROUP=$(id -gn $USER)

        TIMER_CONTENT="[Unit]
Description=ICT Auth Timer - $VERSION

[Timer]
OnBootSec=1min
OnUnitActiveSec=1min

[Install]
WantedBy=timers.target"

        SERVICE_CONTENT="[Unit]
Description=ICT Auth Service - $VERSION
After=network.target

[Service]
Type=oneshot
ExecStart=/bin/bash -c 'source $VENV_DIR/bin/activate && python3 $INSTALL_DIR/service.py'
User=$USER
Group=$GROUP
EnvironmentFile=$INSTALL_DIR/.env

[Install]
WantedBy=multi-user.target"

        FRPC_CONTENT="[Unit]
Description=frpc Service

[Service]
Type=simple
ExecStart=$FRPC_COMMAND
User=root
Group=root

[Install]
WantedBy=multi-user.target"

        echo "$TIMER_CONTENT" | sudo tee "/etc/systemd/system/ict_auth.timer" > /dev/null
        echo "$SERVICE_CONTENT" | sudo tee "/etc/systemd/system/ict_auth.service" > /dev/null
        echo "$FRPC_CONTENT" | sudo tee "/etc/systemd/system/frpc.service" > /dev/null

        sudo systemctl daemon-reload
        sudo systemctl start ict_auth.timer
        sudo systemctl enable ict_auth.timer

        echo "[INFO] Persistent connection service started successfully."
    fi
}

function service_disable() {
    if systemctl list-timers | grep -q "ict_auth.timer"; then
        echo "[INFO] Stopping persistent connection service..."
        
        sudo systemctl stop ict_auth.timer
        sudo systemctl disable ict_auth.timer

        sudo systemctl stop ict_auth.service
        sudo systemctl disable ict_auth.service

        sudo systemctl stop frpc.service

        sudo rm -f "/etc/systemd/system/ict_auth.service"
        sudo rm -f "/etc/systemd/system/ict_auth.timer"
        sudo rm -f "/etc/systemd/system/frpc.service"

        sudo systemctl daemon-reload

        rm -f "$INSTALL_DIR/.env"

        echo "[INFO] Persistent connection service stopped successfully."
    else
        echo "[INFO] Persistent connection service has not been enabled."
    fi
}


case "$1" in
    "") 
        source "$VENV_DIR/bin/activate"
        python3 "$INSTALL_DIR/ict_auth.py"
        ;;
    "--help") 
        show_help
        ;;
    "--enable")
        service_enable
        ;;
    "--disable")
        service_disable
        ;;
    "--log")
        journalctl -u ict_auth.service | grep "bash"
        ;;
    "--uninstall") 
        if systemctl list-timers | grep -q "ict_auth.timer"; then
            service_disable
        fi
        rm -f "$BIN_DIR/ict_auth"
        rm -rf "$INSTALL_DIR"
        echo "[INFO] ict_auth uninstalled successfully"
        ;;
    "--version")
        cat "$INSTALL_DIR/version.txt"
        ;;
    *) 
        echo "Unknown argument: $1"
        show_help
        ;;
esac