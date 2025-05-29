import logging
import os
from pathlib import Path

from .core import WebManager

logger = logging.getLogger("ict_auth")

TEST_URL = "https://google.com"


def test() -> None:
    try:
        with WebManager(TEST_URL):
            logger.info("Pass")
    except Exception as e:
        logger.setLevel(logging.DEBUG)
        logger.debug(f"Exception: {e}")
        logger.debug(
            f"PLAYWRIGHT_BROWSERS_PATH = {os.environ.get('PLAYWRIGHT_BROWSERS_PATH')}"
        )
        logger.debug(f"LD_LIBRARY_PATH = {os.environ.get('LD_LIBRARY_PATH')}")
        whl_files = list(Path("dist").glob("*.whl"))
        for file in whl_files:
            logger.debug(f"whl file: {file} size: {file.stat().st_size} bytes")

        def list_all_files(dir_path: Path, indent: int = 0):
            for item in dir_path.iterdir():
                logger.debug("  " * indent + item.name)
                if item.is_dir():
                    list_all_files(item, indent + 1)

        list_all_files(Path(__file__).parent)
        exit(1)
