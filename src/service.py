import os
import sys
import time
import logging

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from ict_auth import (
    _login,
    _logout,
    check_login,
    get_driver,
    show_debug_info,
    NetworkError,
    URL,
)

logging.basicConfig(
    filename=f"{os.path.expanduser('~')}/.local/ict_auth/service.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def verify():
    try:
        driver = get_driver()
        if check_login(driver):
            _logout(driver)
        _login(driver, ict_username, ict_password)
        try:
            driver.find_element(By.CSS_SELECTOR, "#username.value")
        except NoSuchElementException:
            exit(1)
    except NetworkError:
        raise
    except Exception:
        logger.error(
            "An internal error has occurred. Please contact the developer and provide the information below."
        )
        show_debug_info()
        raise
    finally:
        driver.quit()


def service():
    logger.info("Service Start.")
    try:
        while True:
            try:
                driver = get_driver()
                if not check_login(driver):
                    logger.info(
                        "Connection interruption detected. Logging in automatically."
                    )
                    _login(driver, ict_username, ict_password)
                    # fmt: off
                    username = driver.find_element(By.CSS_SELECTOR, "#username.value").text
                    usedflow = driver.find_element(By.CSS_SELECTOR, "#used-flow.value").text
                    usedtime = driver.find_element(By.CSS_SELECTOR, "#used-time.value").text
                    ipv4 = driver.find_element(By.CSS_SELECTOR, "#ipv4.value").text
                    logger.info(f"Username: {username}")
                    logger.info(f"Used flow: {usedflow}")
                    logger.info(f"Used time: {usedtime}")
                    logger.info(f"IP address: {ipv4}")
                    # fmt: on
                driver.quit()
                time.sleep(60)
            except NetworkError:
                logger.warning(f"Unable to access {URL}. Retrying in 10 minutes.")
                driver.quit()
                time.sleep(600)
    except Exception:
        logger.exception(
            "An internal error has occurred. Please contact the developer and provide the information below."
        )
        show_debug_info(logger)
        sys.exit(1)
    finally:
        logger.info("Service Exit.")


if __name__ == "__main__":

    ict_username = os.getenv("ICT_USERNAME")
    ict_password = os.getenv("ICT_PASSWORD")

    if "--check" in sys.argv:
        verify()
    else:
        service()
