import logging
import os
from pathlib import Path
from typing import Dict

from playwright.sync_api import Page, sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeout
from rich.prompt import Prompt

URL = "https://gw.ict.ac.cn"
logger = logging.getLogger("ict_auth")
debug = os.getenv("DEBUG", "0")


class WebManager:
    def __init__(self, url: str = URL):
        self.url = url
        self.page: Page = None

    def env_set(self):
        """
        Initialize required environment variables.
        """
        os.environ.pop("http_proxy", None)
        os.environ.pop("https_proxy", None)
        os.environ.pop("HTTP_PROXY", None)
        os.environ.pop("HTTPS_PROXY", None)

        path = Path(__file__).parent
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(path / "browser")
        os.environ["LD_LIBRARY_PATH"] = str(path / "libs")

    def __enter__(self):
        self.env_set()
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch()
        self.page = self.browser.new_page()
        self.page.goto(self.url)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if self.browser:
                self.browser.close()
        except Exception:
            pass
        finally:
            try:
                if self.playwright:
                    self.playwright.stop()
            except Exception:
                pass

    def is_logged_in(self) -> bool:
        try:
            self.page.locator("#logout.btn-logout").wait_for(
                state="visible", timeout=2000
            )
            return True
        except PlaywrightTimeout:
            return False

    def login(self, username: str, password: str):
        self.page.fill("#username.input-box", username)
        self.page.fill("#password.input-box", password)
        btn_login = self.page.locator("#login-account.btn-login")
        btn_login.scroll_into_view_if_needed()
        btn_login.click()

        try:
            self.page.locator("#logout.btn-logout").wait_for(
                state="visible", timeout=2000
            )
            logger.info("✅ Login successfully")
            self.print_info()
        except PlaywrightTimeout as e:
            logger.error("❌ Login failed.")
            if debug == "1":
                self.page.screenshot(path="screenshot.png")
            logger.debug("Screenshot saved as screenshot.png")
            logger.debug(f"Login failed with error: {e}", exc_info=True)

    def logout(self):
        btn_logout = self.page.locator("#logout.btn-logout")
        btn_logout.scroll_into_view_if_needed()
        btn_logout.click()
        self.page.get_by_role("button", name="确认").click()

        try:
            self.page.locator("#login-account.btn-login").wait_for(
                state="visible", timeout=2000
            )
            logger.info("✅ Logout successfully")
        except PlaywrightTimeout:
            logger.error("❌ Logout failed")

    def print_info(self):
        username = self.page.locator("#username.value").inner_text()
        usedflow = self.page.locator("#used-flow.value").inner_text()
        usedtime = self.page.locator("#used-time.value").inner_text()
        ip = self.page.locator("#ipv4.value").inner_text()
        logger.info(f"User: {username}")
        logger.info(f"Used flow: {usedflow}")
        logger.info(f"Used time: {usedtime}")
        logger.info(f"IP: {ip}")


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


def main():
    """
    Check the status of the user.
    If not logged in, prompt for username and password.
    If logged in, prompt for logout.
    """
    try:
        logger.info("Initializing Runtime...")
        with WebManager() as web:
            if web.is_logged_in():
                logger.info(
                    "Status: [bold green]Online[/bold green]", extra={"markup": True}
                )
                web.print_info()
                ask_logout = Prompt.ask(
                    "Do you want to log out?", choices=["yes", "no"], default="no"
                )
                if ask_logout.lower() == "yes":
                    web.logout()
            else:
                logger.info(
                    "Status: [bold red]Offline[/bold red]", extra={"markup": True}
                )
                logger.info("Starting login process...")
                account = ask_for_account()
                web.login(account["username"], account["password"])
    except KeyboardInterrupt:
        print()
