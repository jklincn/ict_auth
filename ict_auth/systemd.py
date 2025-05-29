#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
from pathlib import Path
from typing import Dict, Optional

USER_SYSTEMD_DIR = Path.home() / ".config" / "systemd" / "user"
USER_SYSTEMD_DIR.mkdir(parents=True, exist_ok=True)


def _run_systemctl_command(args: list) -> bool:
    try:
        subprocess.run(
            ["systemctl", "--user"] + args,
            capture_output=True,
            text=True,
            check=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Failed to execute systemctl command")
        print(f"command: {e.cmd}")
        print(f"Exit code: {e.returncode}")
        print(f"stdout:\n{e.stdout}")
        print(f"stderr:\n{e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Error occurred while executing command: {e}")
        return False


def create_service(
    service_name: str,
    executable_path: str,
    description: str = "",
    working_directory: Optional[str] = None,
    environment_vars: Optional[Dict[str, str]] = None,
    restart_policy: str = "on-failure",
    RestartSec: int = 5,
) -> bool:

    service_file = USER_SYSTEMD_DIR / f"{service_name}.service"

    service_content = "[Unit]\n"
    service_content += f"Description={description or service_name}\n"
    service_content += "After=network.target\n\n"

    service_content += "[Service]\n"
    service_content += "Type=simple\n"
    service_content += f"ExecStart={executable_path}\n"
    service_content += f"Restart={restart_policy}\n"
    if restart_policy == "always":
        service_content += f"RestartSec={RestartSec}\n"

    if working_directory:
        service_content += f"WorkingDirectory={working_directory}\n"

    if environment_vars:
        for key, value in environment_vars.items():
            service_content += f"Environment={key}={value}\n"

    service_content += "\n[Install]\n"
    service_content += "WantedBy=default.target\n"

    with open(service_file, "w", encoding="utf-8") as f:
        f.write(service_content)

    daemon_reload()
    return True


def enable_service(service_name: str):
    assert _run_systemctl_command(["enable", f"{service_name}.service"])


def disable_service(service_name: str):
    assert _run_systemctl_command(["disable", f"{service_name}.service"])


def start_service(service_name: str):
    assert _run_systemctl_command(["start", f"{service_name}.service"])


def stop_service(service_name: str):
    assert _run_systemctl_command(["stop", f"{service_name}.service"])


def restart_service(service_name: str):
    assert _run_systemctl_command(["restart", f"{service_name}.service"])


def daemon_reload():
    assert _run_systemctl_command(["daemon-reload"])


def remove_service(service_name: str):
    service_file = USER_SYSTEMD_DIR / f"{service_name}.service"
    if service_file.exists():
        service_file.unlink()
        stop_service(service_name)
        disable_service(service_name)
        daemon_reload()
    return True
