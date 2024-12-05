#!/usr/bin/env bash

INSTALL_DIR="$HOME/.local/ict_auth"
BIN_DIR="$HOME/.local/bin"
VENV_DIR="$INSTALL_DIR/venv"

if [ "$EUID" -eq 0 ]; then
    SUDO=""
else
    SUDO="sudo"
fi

function show_help() {
    echo "Usage: ict_auth [OPTIONS] COMMAND"
    echo ""
    echo "A command-line tool for ICT network authentication."
    echo ""
    echo "Options:"
    echo "  -h, --help          Show this help message and exit"
    echo "  -V, --version       Show version information and exit"
    echo ""
    echo "Commands:"
    echo "  login               Log in to the ICT network"
    echo "  logout              Log out and terminate the session"
    echo "  enable              Enable and start the persistent connection service"
    echo "  disable             Disable the persistent connection service"
    echo "  logs                Show logs for the persistent connection service"
    echo "  uninstall           Uninstall ict_auth from the system"
}

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

        USER="$USER"
        GROUP=$(id -gn $USER)

        TIMER_CONTENT="[Unit]
Description=ICT Auth Timer

[Timer]
OnBootSec=1min
OnUnitActiveSec=1min

[Install]
WantedBy=timers.target"

        SERVICE_CONTENT="[Unit]
Description=ICT Auth Service
After=network.target

[Service]
Type=oneshot
ExecStart=/bin/bash -c 'source $VENV_DIR/bin/activate && python3 $INSTALL_DIR/service.py'
User=$USER
Group=$GROUP
EnvironmentFile=$INSTALL_DIR/.env

[Install]
WantedBy=multi-user.target"

        echo "$TIMER_CONTENT" | sudo tee "/etc/systemd/system/ict_auth.timer" > /dev/null
        echo "$SERVICE_CONTENT" | sudo tee "/etc/systemd/system/ict_auth.service" > /dev/null

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

        sudo rm -f "/etc/systemd/system/ict_auth.service"
        sudo rm -f "/etc/systemd/system/ict_auth.timer"

        sudo systemctl daemon-reload

        rm -f "$INSTALL_DIR/.env"

        echo "[INFO] Persistent connection service stopped successfully."
    else
        echo "[INFO] Persistent connection service has not been enabled."
    fi
}


case "$1" in
    ""|"--help"|"-h") 
        show_help
        ;;
    "--version"|"-V") 
        if [[ -f "$INSTALL_DIR/release.txt" ]]; then
            cat "$INSTALL_DIR/release.txt"
        else
            cat "$INSTALL_DIR/self-build.txt"
        fi
        ;;
    "login")
        source "$VENV_DIR/bin/activate"
        python3 "$INSTALL_DIR/ict_auth.py" login
        ;;
    "logout")
        source "$VENV_DIR/bin/activate"
        python3 "$INSTALL_DIR/ict_auth.py" logout
        ;;
    "enable")
        service_enable
        ;;
    "disable")
        service_disable
        ;;   
    "logs")
        journalctl -u ict_auth.service | grep "bash"
        ;;
    "uninstall") 
        if systemctl list-timers | grep -q "ict_auth.timer"; then
            service_disable
        fi
        rm -f "$BIN_DIR/ict_auth"
        rm -rf "$INSTALL_DIR"
        echo "[INFO] ict_auth uninstalled successfully."
        ;;
    *) 
        echo "[ERROR] Unknown command: $1"
        show_help
        ;;
esac