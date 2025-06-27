# ict_auth/service.py
import logging
import os
import signal
import sys
import time
import traceback

from .core import WebManager
from .logger import configure_logging

configure_logging("service")
logger = logging.getLogger("ict_auth")


def handle_exit(signum, frame):
    logger.info("ICT Auth service stopped.")
    logger.debug(f"Signal received: {signum}")
    stack = "".join(traceback.format_stack(frame))
    logger.debug("Stack trace at shutdown:\n" + stack)
    sys.exit(0)


def main():
    signal.signal(signal.SIGTERM, handle_exit)
    logger.info("ICT Auth service started.")
    username = os.environ.get("username")
    password = os.environ.get("password")

    try:
        while True:
            with WebManager() as web:
                if not web.is_logged_in():
                    logger.info("Connection interrupted. Attempting automatic login.")
                    web.login(username, password)
            time.sleep(60)
    except Exception as e:
        logger.exception("Unhandled exception in main loop. Exiting.")
        raise


if __name__ == "__main__":
    main()
