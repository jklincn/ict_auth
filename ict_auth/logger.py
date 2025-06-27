# ict_auth/logger.py

import logging
import os
from pathlib import Path
from typing import Literal

from rich.logging import RichHandler


def configure_logging(mode: Literal["cli", "service"]):
    root_logger = logging.getLogger("ict_auth")
    debug = os.getenv("DEBUG", "0")
    level = logging.DEBUG if debug == "1" else logging.INFO
    root_logger.setLevel(level)

    if root_logger.hasHandlers():
        return

    if mode == "cli":
        handler = RichHandler(
            show_level=False,
            show_path=False,
            show_time=False,
            level=level,
        )
        formatter = logging.Formatter("[%(levelname)s] %(message)s")
    else:
        log_file_path = Path(__file__).parent / "ict_auth.log"
        handler = logging.FileHandler(log_file_path, encoding="utf-8")
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
