#!/usr/bin/env bash

VERSION="2024-09-27"
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
    echo "  ict_auth            Start Internet authentication"
    echo "  ict_auth uninstall  Uninstall ict_auth from the system"
    echo "  ict_auth version    Print version information"
}

# Install
if [ ! -d "$INSTALL_DIR" ]; then
    check_deps
    mkdir -p "$BIN_DIR" "$INSTALL_DIR"
    cp -r "$SCRIPT_DIR"/* "$INSTALL_DIR/"
    ln -sf "$INSTALL_DIR/setup.sh" "$BIN_DIR/ict_auth"
    if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
        echo "WARNING: $BIN_DIR is not in your PATH. You may need to add it."
    fi
    echo "ict_auth successfully installed in $INSTALL_DIR"
    exit 0
fi

if [ -z "$1" ]; then
    check_deps
    python3 "$INSTALL_DIR/ict_auth.py"
else
    if [ "$1" == "uninstall" ]; then
        rm -f "$BIN_DIR/ict_auth"
        rm -rf "$INSTALL_DIR"
        echo "ict_auth uninstalled successfully"
    elif [ "$1" == "version" ]; then
        echo "$VERSION"
    else
        echo "Unknown argument: $1"
        show_help
    fi
fi