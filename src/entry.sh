#!/usr/bin/env bash

install_dir="$HOME/.local/ict_auth"
bin_dir="$HOME/.local/bin"
venv_dir="$install_dir/venv"

sudo_cmd() {
    if [ "$EUID" -eq 0 ]; then
        "$@"
    else
        sudo "$@"
    fi
}

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
    echo "  status              Show the current login status"
    echo "  enable              Enable and start the persistent connection service"
    echo "  disable             Disable the persistent connection service"
    echo "  logs                Show logs for the persistent connection service"
    echo "  upgrade             Check for updates and install the latest version"
    echo "  uninstall           Uninstall ict_auth from the system"
}

function service_enable() {
    if systemctl list-units | grep -q "ict_auth.service"; then
        echo "[INFO] Persistent connection service has been enabled."
    else
        echo "[INFO] Starting persistent connection service..."
        echo "============================="
        read -ep "ICT Username: " ict_username
        read -esp "ICT Password: " ict_password
        echo
        echo "============================="

        echo "[INFO] Verifying account..."
        source "$venv_dir/bin/activate"
        ICT_USERNAME=$ict_username ICT_PASSWORD=$ict_password python3 "$install_dir/service.py" --check
        
        if [ $? -ne 0 ]; then
            echo "[ERROR] Account verification failed."
            echo "[INFO] Please check your username and password and try again."
            exit 1
        else
            echo "[INFO] Account verified successfully."
        fi

        echo "ICT_USERNAME=$ict_username" > "$install_dir/.env"
        echo "ICT_PASSWORD=$ict_password" >> "$install_dir/.env"
        chmod 600 "$install_dir/.env"

        user="$USER"
        group=$(id -gn $USER)

        service_content="[Unit]
Description=ICT Auth Service
After=network.target

[Service]
Type=simple

User=$user
Group=$group
EnvironmentFile=$install_dir/.env

ExecStartPre=/bin/bash -c 'resolvectl flush-caches'
ExecStart=/bin/bash -c 'source $venv_dir/bin/activate && python3 $install_dir/service.py'

[Install]
WantedBy=multi-user.target"

        echo "$service_content" | sudo_cmd tee "/etc/systemd/system/ict_auth.service" > /dev/null

        sudo_cmd systemctl daemon-reload
        sudo_cmd systemctl start ict_auth.service
        sudo_cmd systemctl enable ict_auth.service

        echo "[INFO] Persistent connection service started successfully."
    fi
}

function service_disable() {
    if systemctl list-units | grep -q "ict_auth.service"; then
        echo "[INFO] Stopping persistent connection service..."

        sudo_cmd systemctl stop ict_auth.service
        sudo_cmd systemctl disable ict_auth.service

        sudo_cmd rm -f "/etc/systemd/system/ict_auth.service"

        sudo_cmd systemctl daemon-reload

        rm -f "$install_dir/.env"

        echo "[INFO] Persistent connection service stopped successfully."
    else
        echo "[INFO] Persistent connection service has not been enabled."
    fi
}

function upgrade() {
    latest=$(curl -s https://oss.jklincn.com/ict_auth/release.txt)
    # not consider self-build
    if [[ -f "$install_dir/release.txt" ]]; then
        current=$(cat "$install_dir/release.txt")
        if [[ $latest == $current ]]; then
            echo "[INFO] The current version is already the latest version."
            return
        else
            echo "[INFO] Upgrading from $current to $latest..."
        fi
    fi
    echo "[INFO] Downloading installer..."
    if ! curl -f --progress-bar -o /tmp/ict_auth.run https://oss.jklincn.com/ict_auth/ict_auth.run; then
        echo "[ERROR] Failed to download installer."
        exit 1
    fi
    chmod +x /tmp/ict_auth.run
    echo "y" | /tmp/ict_auth.run
    if [[ $? -eq 0 ]]; then
        echo "[INFO] Upgrade completed successfully."
    else
        echo "[ERROR] Upgrade failed."
        exit 1
    fi
}

case "$1" in
    ""|"--help"|"-h") 
        show_help
        ;;
    "--version"|"-V") 
        if [[ -f "$install_dir/release.txt" ]]; then
            cat "$install_dir/release.txt"
        else
            cat "$install_dir/self-build.txt"
        fi
        ;;
    "login")
        source "$venv_dir/bin/activate"
        python3 "$install_dir/ict_auth.py" login
        ;;
    "logout")
        source "$venv_dir/bin/activate"
        python3 "$install_dir/ict_auth.py" logout
        ;;
    "status")
        source "$venv_dir/bin/activate"
        python3 "$install_dir/ict_auth.py" status
        ;;
    "enable")
        service_enable
        ;;
    "disable")
        service_disable
        ;;   
    "logs")
        less "$install_dir/log"
        ;;
    "upgrade")
        upgrade
        ;;
    "uninstall") 
        if systemctl list-units | grep -q "ict_auth.service"; then
            service_disable
        fi
        rm -f "$bin_dir/ict_auth"
        rm -rf "$install_dir"
        sed -i '/source .*ict_auth-completion.bash/d' ~/.bash_completion
        echo "[INFO] ict_auth uninstalled successfully."
        ;;
    *) 
        echo "[ERROR] Unknown command: $1"
        show_help
        ;;
esac