import logging
import signal
import time
from pathlib import Path

logging.basicConfig(
    filename=Path(__file__).parent / "ict_auth.log",
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def handle_exit(signum, frame):
    logger.info("ICT Auth service stopped.")
    exit(0)


signal.signal(signal.SIGTERM, handle_exit)

logger.info("ICT Auth service started.")
while True:
    logger.info("ICT Auth service is running...")
    time.sleep(10)
