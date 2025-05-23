#!/usr/bin/env bash

set -euo pipefail

python3 -m ensurepip --user

uv init 
uv add playwright
PLAYWRIGHT_BROWSERS_PATH=0 uv run -- playwright install --with-deps chromium-headless-shell
uv run -- pyinstaller -F main.py
