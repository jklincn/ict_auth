# ict_auth/logger.py

import logging
from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
    handlers=[
        RichHandler(
            show_level=False,
            show_path=False,
            show_time=False,
        )
    ],
)

logger = logging.getLogger("ict_auth")
