#!/usr/bin/env bash

set -e

script_dir=$(cd "$(dirname "$0")" && pwd)
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

function cleanup() {
    rm -f "$bin_dir/ict_auth"
    rm -rf "$install_dir"
    exit 1
}

function install() {
    trap cleanup SIGINT
    echo "[INFO] Installing ICT Auth..."

    mkdir -p "$install_dir" "$bin_dir"
    cp -r "$script_dir"/* "$install_dir/"
    echo "source $install_dir/ict_auth-completion.bash" >> ~/.bash_completion
    ln -sf "$install_dir/entry.sh" "$bin_dir/ict_auth"

    packages=(
        python3
        python3-pip
        python3-venv
        bash-completion
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
            sudo_cmd apt-get update
            echo "[INFO] Installing missing packages: ${missing_packages[*]}"
            sudo_cmd apt-get install -y "${missing_packages[@]}"
        else
            echo "[INFO] Installation of missing packages aborted."
            exit 0
        fi
    fi

    /usr/bin/python3 -m venv "$venv_dir"

    source "$venv_dir/bin/activate"

    pip install -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple selenium -q

    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to install dependency."
        rm -f "$bin_dir/ict_auth"
        rm -rf "$install_dir"
        exit 1
    fi

    if [[ ":$PATH:" != *":$bin_dir:"* ]]; then
        echo -e "\e[33m[WARNING] $bin_dir is not in your PATH.\e[0m"
        echo "Run the following command to add it to your PATH temporarily:"
        echo "  export PATH=\"$bin_dir:\$PATH\""
    fi

    . /etc/bash_completion
    echo "[INFO] ict_auth successfully installed in $install_dir"
    exit 0
}

# Install
if [ ! -d "$install_dir" ]; then
    install
else
    if [[ -f "$install_dir/release.txt" ]]; then
        version=$(cat $install_dir/release.txt)
    else
        version=$(cat $install_dir/self-build.txt)
    fi    
    read -p "[INFO] ICT Auth (version: $version) is already installed on this system. Would you like to overwrite it? [y/N]" choice
    choice=${choice:-n}
    if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
        rm -f "$install_dir"/release.txt "$install_dir"/self-build.txt
        cp -r "$script_dir"/* "$install_dir/"
        if [ $? -ne 0 ]; then
            echo "[ERROR] Failed to overwrite."
            exit 1
        fi
        sudo_cmd systemctl restart ict_auth.service
        echo "[INFO] ict_auth successfully installed in $install_dir"
    else
        echo "[INFO] Exit."
    fi
fi