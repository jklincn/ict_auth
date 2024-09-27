#!/usr/bin/env bash

BIN_DIR="$HOME/.local/bin"
INSTALL_DIR="$HOME/.local/ict_auth"
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)

if [ "$EUID" -eq 0 ]; then
    SUDO=""
else
    SUDO="sudo"
fi

function check_deps(){
    echo "Checking dependencies..."
    packages=(
        python3-pip
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
        read -p "Do you want to install these packages? (Y/n): " choice
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
    
    if ! python3 -m pip list 2>/dev/null | grep -F selenium >/dev/null 2>&1; then
        echo "selenium is not installed. Installing selenium..."
        python3 -m pip install --no-index --find-links="$SCRIPT_DIR/wheel" selenium
    fi
}

function show_help() {
    echo "Usage:"
    echo "  ict_auth              Start Internet authentication"
    echo "  ict_auth --help       Show help message"
    echo "  ict_auth --uninstall  Uninstall ict_auth from the system"
    echo "  ict_auth --version    Print version information"
}

# Install
if [ ! -d "$INSTALL_DIR" ]; then
    check_deps
    mkdir -p "$BIN_DIR" "$INSTALL_DIR"
    cp -r "$SCRIPT_DIR"/* "$INSTALL_DIR/"
    ln -sf "$INSTALL_DIR/setup.sh" "$BIN_DIR/ict_auth"
    if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
        echo -e "\e[33mWARNING: $BIN_DIR is not in your PATH. Please re-login to apply the changes.\e[0m"
    fi
    echo "ict_auth successfully installed in $INSTALL_DIR"
    exit 0
fi

case "$1" in
    "") 
        check_deps
        python3 "$INSTALL_DIR/ict_auth.py"
        ;;
    "--help") 
        show_help
        ;;
    "--uninstall") 
        rm -f "$BIN_DIR/ict_auth"
        rm -rf "$INSTALL_DIR"
        echo "ict_auth uninstalled successfully"
        ;;
    "--version")
        if [ -f "$INSTALL_DIR"/version.txt ]; then
            cat "$INSTALL_DIR"/version.txt
        else
            echo "Self-Building"
        fi
        ;;
    *) 
        echo "Unknown argument: $1"
        show_help
        ;;
esac