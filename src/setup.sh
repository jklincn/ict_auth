#!/usr/bin/env bash

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

need_install=false

for pkg in "${packages[@]}"; do
    if ! dpkg -s "$pkg" >/dev/null 2>&1; then
        need_install=true
        break
    fi
done

if [ "$need_install" = true ]; then
    echo "Updating package lists..."
    sudo apt update

    for pkg in "${packages[@]}"; do
        if ! dpkg -s "$pkg" >/dev/null 2>&1; then
            echo "Installing $pkg..."
            sudo apt-get install -y "$pkg"
        fi
    done
fi

if ! python3 -m pip list 2>/dev/null | grep -F selenium >/dev/null 2>&1; then
    echo "selenium is not installed. Installing selenium..."
    python3 -m pip install --no-index --find-links=$(pwd)/wheel selenium
fi

python3 $(realpath "$(dirname "$0")")/ict_auth.py