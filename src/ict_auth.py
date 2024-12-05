import getpass
import os
import sys
from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
)
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By


class NetworkError(Exception):
    pass


def get_driver() -> WebDriver:
    path = os.path.dirname(os.path.abspath(__file__))

    with open(f"{path}/browser_version.txt", "r") as file:
        version = file.readline().strip()

    options = webdriver.ChromeOptions()
    options.binary_location = f"{path}/chrome/linux64/{version}/chrome"
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = webdriver.ChromeService(
        executable_path=f"{path}/chromedriver/linux64/{version}/chromedriver"
    )

    driver = webdriver.Chrome(options=options, service=service)
    driver.set_page_load_timeout(5)
    driver.implicitly_wait(2)

    return driver


def check_login(driver: WebDriver) -> bool:
    try:
        driver.get("https://gw.ict.ac.cn")
        driver.find_element(By.CSS_SELECTOR, "#logout.btn-logout")
        return True
    except TimeoutException:
        raise NetworkError
    except NoSuchElementException:
        return False


def _logout(driver: WebDriver):
    btn_logout = driver.find_element(By.CSS_SELECTOR, "#logout.btn-logout")
    driver.execute_script("arguments[0].scrollIntoView(true);", btn_logout)
    btn_logout.click()
    confirm_button = driver.find_element(By.CSS_SELECTOR, ".btn-confirm")
    confirm_button.click()


def logout(driver: WebDriver):
    _logout(driver)
    driver.find_element(By.CSS_SELECTOR, "#login-account.btn-login")
    print("[INFO] Logout succeeded.")


def _login(driver: WebDriver, ict_username: str, ict_password: str):
    username = driver.find_element(By.CSS_SELECTOR, "#username.input-box")
    username.send_keys(ict_username)
    password = driver.find_element(By.CSS_SELECTOR, "#password.input-box")
    password.send_keys(ict_password)

    btn_login = driver.find_element(By.CSS_SELECTOR, "#login-account.btn-login")
    driver.execute_script("arguments[0].scrollIntoView(true);", btn_login)
    btn_login.click()


def login(driver: WebDriver):
    print("[INFO] Starting login process...")

    print("=============================")
    ict_username = input("ICT Username: ")
    ict_password = getpass.getpass("ICT Password: ")
    print("=============================")

    _login(driver, ict_username, ict_password)

    # print user info
    try:
        username = driver.find_element(By.CSS_SELECTOR, "#username.value").text
        usedflow = driver.find_element(By.CSS_SELECTOR, "#used-flow.value").text
        usedtime = driver.find_element(By.CSS_SELECTOR, "#used-time.value").text
        ipv4 = driver.find_element(By.CSS_SELECTOR, "#ipv4.value").text
        print("[INFO] Login succeeded.")
        print(f"[INFO] Username: {username}")
        print(f"[INFO] Used flow: {usedflow}")
        print(f"[INFO] Used time: {usedtime}")
        print(f"[INFO] IP address: {ipv4}")
    except NoSuchElementException:
        print("[ERROR] Incorrect username or password.")


def show_debug_info():
    import platform

    path = os.path.dirname(os.path.abspath(__file__))
    try:
        with open(f"{path}/release.txt", "r") as file:
            my_version = file.read().strip()
    except FileNotFoundError:
        with open(f"{path}/self-build.txt", "r") as file:
            my_version = file.read().strip()
    try:
        with open("/etc/os-release", "r") as f:
            for line in f:
                if line.startswith("PRETTY_NAME"):
                    os_version = line.split("=")[1].strip().strip('"')
    except FileNotFoundError:
        os_version = ""
    print(f"Operating System: {os_version}")
    print(f"Python Version: {platform.python_version()}")
    print(f"ICT Auth Version: {my_version}")


if __name__ == "__main__":
    try:
        arg = sys.argv
        if len(arg) != 2:
            raise Exception("len(arg) != 2")
        driver = get_driver()
        print("[INFO] Checking if logged in...")
        is_logged_in = check_login(driver)
        match arg[1]:
            case "login":
                if is_logged_in:
                    print("[INFO] You are already logged in.")
                else:
                    login(driver)
            case "logout":
                if is_logged_in:
                    logout(driver)
                else:
                    print("[ERROR] You are not logged in.")
    except KeyboardInterrupt:
        print()
    except NetworkError:
        print(
            '[ERROR] Unable to access "https://gw.ict.ac.cn". Please check your network connection and try again.'
        )
    except Exception:
        print(
            "\n[INTERNAL ERROR] An internal error has occurred. Please contact the developer and provide the information below."
        )
        show_debug_info()
        raise
    finally:
        driver.quit()
