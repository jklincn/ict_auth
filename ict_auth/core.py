# ict_auth/core.py

import logging
import os
from pathlib import Path

from playwright.sync_api import (
    Page,
    sync_playwright,
)
from playwright.sync_api import (
    TimeoutError as PlaywrightTimeout,
)
from rich.logging import RichHandler
from rich.prompt import Prompt

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

log = logging.getLogger("ict_auth")

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
        log.info("✅ Login successfully")
        print_info(page)
    except PlaywrightTimeout:
        log.error("❌ Login failed")


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
        log.info("✅ Logout successfully")
    except PlaywrightTimeout:
        log.error("❌ Logout failed")


def print_info(page: Page) -> None:
    """
    Get the user information from the page.
    """
    username = page.locator("#username.value").inner_text()
    usedflow = page.locator("#used-flow.value").inner_text()
    usedtime = page.locator("#used-time.value").inner_text()
    ip = page.locator("#ipv4.value").inner_text()
    log.info(f"User: {username}")
    log.info(f"Used flow: {usedflow}")
    log.info(f"Used time: {usedtime}")
    log.info(f"IP: {ip}")


def status(page: Page) -> bool:
    """
    Check the status of the user.
    If not logged in, prompt for username and password.
    If logged in, prompt for logout.
    """
    try:
        page.locator("#logout.btn-logout").wait_for(state="visible", timeout=2000)
        log.info("Status: [bold green]Online[/bold green]", extra={"markup": True})

        print_info(page)
        ask_logout = Prompt.ask(
            "Do you want to log out?", choices=["yes", "no"], default="no"
        )
        if ask_logout.lower() == "yes":
            logout(page)
    except PlaywrightTimeout:
        log.info("Status: [bold red]Offline[/bold red]", extra={"markup": True})
        log.info("Starting login process...")
        username = Prompt.ask("Username")
        password = Prompt.ask("Password", password=True)
        login(page, username, password)


def test() -> None:
    try:
        init()
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto("https://jklincn.com", timeout=5000)
            browser.close()

        log.info("Pass")
    except Exception as e:
        log.setLevel(logging.DEBUG)
        log.debug(f"Exception: {e}")
        log.debug(
            f"PLAYWRIGHT_BROWSERS_PATH = {os.environ.get('PLAYWRIGHT_BROWSERS_PATH')}"
        )
        log.debug(f"LD_LIBRARY_PATH = {os.environ.get('LD_LIBRARY_PATH')}")
        whl_files = list(Path("dist").glob("*.whl"))
        for file in whl_files:
            log.debug(f"whl file: {file} size: {file.stat().st_size} bytes")

        def list_all_files(dir_path: Path, indent: int = 0):
            for item in dir_path.iterdir():
                log.debug("  " * indent + item.name)
                if item.is_dir():
                    list_all_files(item, indent + 1)

        list_all_files(Path(__file__).parent)
        exit(1)


def main() -> None:
    log.info("Initializeing Runtime...")
    init()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(URL, wait_until="load", timeout=2000)
        status(page)
        browser.close()
