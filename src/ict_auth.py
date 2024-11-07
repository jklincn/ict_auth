import getpass
import json
import os

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By


def get_driver() -> WebDriver:
    path = os.path.dirname(os.path.abspath(__file__))

    with open(f"{path}/se-metadata.json", "r") as file:
        data = json.load(file)
    version = data["browsers"][0]["browser_version"]

    options = webdriver.ChromeOptions()
    options.binary_location = f"{path}/chrome/linux64/{version}/chrome"
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = webdriver.ChromeService(
        executable_path=f"{path}/chromedriver/linux64/{version}/chromedriver"
    )

    try:
        driver = webdriver.Chrome(options=options, service=service)
    except Exception as e:
        raise RuntimeError("[ERROR] Failed to initialize WebDriver") from e

    driver.set_page_load_timeout(2)
    driver.implicitly_wait(2)

    return driver


def check_login(driver: WebDriver) -> bool:
    driver.get("https://gw.ict.ac.cn")
    try:
        driver.find_element(By.CSS_SELECTOR, "#logout.btn-logout")
        return True
    except NoSuchElementException:
        return False


def logout(driver: WebDriver):
    btn_logout = driver.find_element(By.CSS_SELECTOR, "#logout.btn-logout")
    if_logout = input("[INFO] You are already logged in. Do you want to logout? [y/N] ")
    if if_logout.lower() == "y":
        driver.execute_script("arguments[0].scrollIntoView(true);", btn_logout)
        btn_logout.click()
        confirm_button = driver.find_element(By.CSS_SELECTOR, ".btn-confirm")
        confirm_button.click()
        driver.find_element(By.CSS_SELECTOR, "#login-account.btn-login")
        print("[INFO] Logout succeeded")


def login(driver: WebDriver):
    print("[INFO] Starting login process...")

    print("=============================")
    ict_username = input("ICT Username: ")
    ict_password = getpass.getpass("ICT Password: ")
    print("=============================")

    username = driver.find_element(By.CSS_SELECTOR, "#username.input-box")
    username.send_keys(ict_username)
    password = driver.find_element(By.CSS_SELECTOR, "#password.input-box")
    password.send_keys(ict_password)

    btn_login = driver.find_element(By.CSS_SELECTOR, "#login-account.btn-login")
    driver.execute_script("arguments[0].scrollIntoView(true);", btn_login)
    btn_login.click()

    # print user info
    try:
        username = driver.find_element(By.CSS_SELECTOR, "#username.value").text
        usedflow = driver.find_element(By.CSS_SELECTOR, "#used-flow.value").text
        usedtime = driver.find_element(By.CSS_SELECTOR, "#used-time.value").text
        ipv4 = driver.find_element(By.CSS_SELECTOR, "#ipv4.value").text
        print("[INFO] Login succeeded")
        print(f"[INFO] Username: {username}")
        print(f"[INFO] Used flow: {usedflow}")
        print(f"[INFO] Used time: {usedtime}")
        print(f"[INFO] IP address: {ipv4}")
    except NoSuchElementException:
        print("[ERROR] Incorrect username or password")


def show_debug_info():
    import platform

    path = os.path.dirname(os.path.abspath(__file__))
    with open(f"{path}/version.txt", "r") as file:
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

    driver = get_driver()

    try:
        print("[INFO] Checking if logged in...")
        if check_login(driver):
            logout(driver)
        else:
            login(driver)
    except KeyboardInterrupt:
        exit(0)
    except Exception as e:
        print(
            "\n[INTERNAL ERROR] An internal error has occurred. Please contact the developer and provide the information below."
        )
        show_debug_info()
        raise
    finally:
        driver.quit()
