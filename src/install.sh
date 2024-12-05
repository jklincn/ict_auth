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

function cleanup() {
    rm -f "$BIN_DIR/ict_auth"
    rm -rf "$INSTALL_DIR"
    exit 1
}

trap cleanup SIGINT

function install() {
    echo "[INFO] Installing ICT Auth..."

    mkdir -p "$INSTALL_DIR" "$BIN_DIR"
    cp -r "$SCRIPT_DIR"/* "$INSTALL_DIR/"
    ln -sf "$INSTALL_DIR/entry.sh" "$BIN_DIR/ict_auth"

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
        echo "[INFO] Missing packages: ${missing_packages[*]}"
        read -p "Do you want to install these packages? [Y/n] " choice
        choice=${choice:-y}
        if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
            echo "[INFO] Updating package lists..."
            $SUDO apt-get update
            echo "[INFO] Installing missing packages: ${missing_packages[*]}"
            $SUDO apt-get install -y "${missing_packages[@]}"
        else
            echo "[INFO] Installation of missing packages aborted."
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
}

# Install
if [ ! -d "$INSTALL_DIR" ]; then
    install
else
    read -p "[INFO] ict_auth is already installed on this system. Would you like to overwrite it? [Y/n]" choice
    choice=${choice:-y}
    if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
        "$BIN_DIR/ict_auth" uninstall
        install
    else
        echo "[INFO] Exit."
    fi
fi