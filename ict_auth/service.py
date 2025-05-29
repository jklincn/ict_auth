# ict_auth/service.py
import logging
import os
import signal
import time

from .core import WebManager
from .logger import configure_logging

configure_logging("service")
logger = logging.getLogger("ict_auth")


def handle_exit(signum, frame):
    logger.info("ICT Auth service stopped.")
    exit(0)


def main():
    signal.signal(signal.SIGTERM, handle_exit)
    logger.info("ICT Auth service started.")
    username = os.environ.get("username")
    password = os.environ.get("password")
    
    while True:
        with WebManager() as web:
            if not web.is_logged_in():
                logger.info("Connection interrupted. Attempting automatic login.")
                web.login(username, password)
        time.sleep(60)


if __name__ == "__main__":
    main()
