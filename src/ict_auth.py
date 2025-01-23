import getpass
import os
import sys
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

URL = "https://gw.ict.ac.cn"


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
    
    retries = 0
    max_retries = 5
    while retries < max_retries:
        try:
            driver = webdriver.Chrome(options=options, service=service)
            driver.set_page_load_timeout(5)
            driver.implicitly_wait(2)
            return driver
        except Exception as e:
            retries += 1
            print(f"[ERROR] Get WebDriver failed, Retrying ({retries+1}/{max_retries})")
            if retries < max_retries:
                time.sleep(1)
            else:
                raise Exception(
                    f"Failed to initialize WebDriver after {max_retries} attempts: {e}"
                )


def check_login(driver: WebDriver) -> bool:
    try:
        driver.get(URL)
    except Exception:
        raise NetworkError
    try:
        driver.find_element(By.CSS_SELECTOR, "#logout.btn-logout")
        return True
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


def show_debug_info(logger=None):
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
    if logger:
        logger.info(f"Operating System: {os_version}")
        logger.info(f"Python Version: {platform.python_version()}")
        logger.info(f"ICT Auth Version: {my_version}")
    else:
        print(f"Operating System: {os_version}")
        print(f"Python Version: {platform.python_version()}")
        print(f"ICT Auth Version: {my_version}")


def status(driver: WebDriver):
    username = driver.find_element(By.CSS_SELECTOR, "#username.value").text
    usedflow = driver.find_element(By.CSS_SELECTOR, "#used-flow.value").text
    usedtime = driver.find_element(By.CSS_SELECTOR, "#used-time.value").text
    ipv4 = driver.find_element(By.CSS_SELECTOR, "#ipv4.value").text

    if os.path.exists("/etc/systemd/system/ict_auth.service"):
        service_status = "active"
    else:
        service_status = "inactive"

    print("[INFO] Status: " + "\033[1;32mOnline\033[0m")
    print(f"[INFO] Service: {service_status}")
    print(f"[INFO] Username: {username}")
    print(f"[INFO] Used flow: {usedflow}")
    print(f"[INFO] Used time: {usedtime}")
    print(f"[INFO] IP address: {ipv4}")


if __name__ == "__main__":
    try:
        arg = sys.argv
        if len(arg) != 2:
            raise Exception("len(arg) != 2")
        print("[INFO] Preparing the runtime...")
        driver = get_driver()
        is_logged_in = check_login(driver)
        if arg[1] == "login":
            if is_logged_in:
                print("[INFO] You are already logged in.")
            else:
                login(driver)
        elif arg[1] == "logout":
            if is_logged_in:
                logout(driver)
            else:
                print("[ERROR] You are not logged in.")
        elif arg[1] == "status":
            if is_logged_in:
                status(driver)
            else:
                # change to systemd status (failed/active/disabled)
                if os.path.exists("/etc/systemd/system/ict_auth.service"):
                    service_status = "active"
                else:
                    service_status = "inactive"
                print("[INFO] Status: " + "\033[1;31mOffline\033[0m")
                print(f"[INFO] Service: {service_status}")

    except KeyboardInterrupt:
        print()
    except NetworkError:
        print(
            f"[ERROR] Unable to access {URL}. Please check your network connection and try again."
        )
    except Exception:
        print(
            "\n[INTERNAL ERROR] An internal error has occurred. Please contact the developer and provide the information below."
        )
        show_debug_info()
        raise
    finally:
        driver.quit()
