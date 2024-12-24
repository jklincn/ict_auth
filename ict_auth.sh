#!/bin/sh

# This is just a helper script to download ICT Auth.

set -u

err() {
    echo "[ERROR]: $1" >&2
    exit 1
}


# Download the installer
latest=$(curl -s https://oss.jklincn.com/ict_auth/release.txt)
echo "[INFO] Downloading ICT Auth installer ($latest)..."
if ! curl -f --progress-bar -o /tmp/ict_auth.run https://oss.jklincn.com/ict_auth/ict_auth.run; then
    err "Failed to download installer"
fi

# Make it executable
chmod +x /tmp/ict_auth.run

# Run the installer with proper TTY handling
if [ ! -t 0 ]; then
    # Script is being piped, connect to TTY for interactive input
    if [ ! -t 1 ]; then
        err "Unable to run interactively"
    fi

    /tmp/ict_auth.run < /dev/tty
else
    # We already have a TTY
    /tmp/ict_auth.run
fi

# Clean up
rm -f /tmp/ict_auth.run