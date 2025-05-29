# ict_auth/core.py
import logging
import os
from pathlib import Path
from typing import Dict

from playwright.sync_api import (
    Page,
    sync_playwright,
)
from playwright.sync_api import (
    TimeoutError as PlaywrightTimeout,
)
from rich.prompt import Prompt

from .logger import logger

URL = "https://gw.ict.ac.cn"


def init() -> None:
    """
    Initialize the Playwright environment.
    """

    # Unset the proxy settings
    os.environ.pop("http_proxy", None)
    os.environ.pop("https_proxy", None)
    os.environ.pop("HTTP_PROXY", None)
    os.environ.pop("HTTPS_PROXY", None)

    # Set the browsers path and library path
    path = Path(__file__).parent
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(path / "browser")
    os.environ["LD_LIBRARY_PATH"] = str(path / "libs")


def login(page: Page, username: str, password: str) -> None:
    """
    Login to the ICT network using the provided username and password.
    """
    page.fill("#username.input-box", username)
    page.fill("#password.input-box", password)
    btn_login = page.locator("#login-account.btn-login")
    btn_login.scroll_into_view_if_needed()
    btn_login.click()

    # Confirm login
    try:
        page.locator("#logout.btn-logout").wait_for(state="visible", timeout=2000)
        logger.info("✅ Login successfully")
        print_info(page)
    except PlaywrightTimeout:
        logger.error("❌ Login failed")


def ask_for_account() -> Dict[str, str]:
    """
    Prompt the user for ICT account.
    """
    print("=============================")
    username = Prompt.ask("Username")
    password = Prompt.ask("Password", password=True)
    print("=============================")
    return {
        "username": username,
        "password": password,
    }


def logout(page: Page) -> None:
    btn_logout = page.locator("#logout.btn-logout")
    btn_logout.scroll_into_view_if_needed()
    btn_logout.click()

    # Handle double confirmation
    confirm_button = page.locator(".btn-confirm")
    confirm_button.click()

    # Confirm logout
    try:
        page.locator("#login-account.btn-login").wait_for(state="visible", timeout=2000)
        logger.info("✅ Logout successfully")
    except PlaywrightTimeout:
        logger.error("❌ Logout failed")


def print_info(page: Page) -> None:
    """
    Get the user information from the page.
    """
    username = page.locator("#username.value").inner_text()
    usedflow = page.locator("#used-flow.value").inner_text()
    usedtime = page.locator("#used-time.value").inner_text()
    ip = page.locator("#ipv4.value").inner_text()
    logger.info(f"User: {username}")
    logger.info(f"Used flow: {usedflow}")
    logger.info(f"Used time: {usedtime}")
    logger.info(f"IP: {ip}")


def check_login(page: Page) -> bool:
    """
    Check if the user is logged in.
    Returns True if logged in, False otherwise.
    """
    try:
        page.locator("#logout.btn-logout").wait_for(state="visible", timeout=2000)
        return True
    except PlaywrightTimeout:
        return False


def main(page: Page):
    """
    Check the status of the user.
    If not logged in, prompt for username and password.
    If logged in, prompt for logout.
    """
    if check_login(page):
        logger.info("Status: [bold green]Online[/bold green]", extra={"markup": True})
        print_info(page)
        ask_logout = Prompt.ask(
            "Do you want to log out?", choices=["yes", "no"], default="no"
        )
        if ask_logout.lower() == "yes":
            logout(page)
    else:
        logger.info("Status: [bold red]Offline[/bold red]", extra={"markup": True})
        logger.info("Starting login process...")
        account = ask_for_account()
        login(page, account["username"], account["password"])


def ci_test() -> None:
    try:
        init()
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto("https://jklincn.com", timeout=5000)
            browser.close()
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


def entry() -> None:
    logger.info("Initializeing Runtime...")
    init()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(URL, wait_until="load", timeout=2000)
        main(page)
        browser.close()
