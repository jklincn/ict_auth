#!/usr/bin/env bash

BIN_DIR="$HOME/.local/bin"
TARGET_DIR="$HOME/.local/ict_auth"
SCRIPT_DIR=$(dirname "$(realpath "$0")")

if [ "$SCRIPT_DIR" == "$BIN_DIR" ]; then
    ROOT_DIR="$TARGET_DIR"
else
    ROOT_DIR="$SCRIPT_DIR"
fi

if [ "$1" == "install" ]; then
    mkdir -p "$BIN_DIR" "$TARGET_DIR"
    cp -r * "$TARGET_DIR/"
    ln -sf "$TARGET_DIR/setup.sh" "$BIN_DIR/ict_auth"
    if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
        echo "WARNING: $BIN_DIR is not in your PATH. You may need to add it."
    fi
    echo "ict_auth installed successfully"
elif [ "$1" == "uninstall" ]; then
    rm -f "$BIN_DIR/ict_auth"
    rm -rf "$TARGET_DIR"
    echo "ict_auth uninstalled successfully"
else
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
    )

    missing_packages=()

    for pkg in "${packages[@]}"; do
        if ! dpkg -s "$pkg" >/dev/null 2>&1; then
            missing_packages+=("$pkg")
        fi
    done

    if [ ${#missing_packages[@]} -gt 0 ]; then
        echo "Missing packages detected: ${missing_packages[*]}"
        read -p "Do you want to install these packages? (Y/n): " choice
        choice=${choice:-y}
        if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
            echo "Updating package lists..."
            sudo apt-get update
            echo "Installing missing packages: ${missing_packages[*]}"
            sudo apt-get install -y "${missing_packages[@]}"
        else
            echo "Installation of missing packages aborted."
            exit 0
        fi

    if ! python3 -m pip list 2>/dev/null | grep -F selenium >/dev/null 2>&1; then
        echo "selenium is not installed. Installing selenium..."
        python3 -m pip install --no-index --find-links="$ROOT_DIR/wheel" selenium
    fi

    python3 "$ROOT_DIR/ict_auth.py"
fi
