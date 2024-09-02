import getpass
import json
import os

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

if __name__ == "__main__":
    path = os.path.dirname(os.path.abspath(__file__))

    with open(f"{path}/se-metadata.json", "r") as file:
        data = json.load(file)
    version = data["browsers"][0]["browser_version"]

    options = webdriver.ChromeOptions()
    options.binary_location = f"{path}/chrome/linux64/{version}/chrome"
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"--user-data-dir=/tmp/ict_auth")

    service = webdriver.ChromeService(
        executable_path=f"{path}/chromedriver/linux64/{version}/chromedriver"
    )

    driver = webdriver.Chrome(options=options, service=service)
    driver.implicitly_wait(5)

    try:
        print("Checking if logged in...")
        driver.get("https://gw.ict.ac.cn")
        btn_logout = driver.find_element(By.CSS_SELECTOR, "#logout.btn-logout")
        if_logout = input("You are already logged in. Do you want to logout? [y/N] ")
        if if_logout.lower() == "y":
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", btn_logout)
                btn_logout.click()
                confirm_button = driver.find_element(By.CSS_SELECTOR, ".btn-confirm")
                confirm_button.click()
                driver.find_element(By.CSS_SELECTOR, "#login-account.btn-login")
                print("Logout succeeded")
            except BaseException as e:
                print(f"Logout Internal error: {e}")

    except NoSuchElementException:
        print("Starting login...")
        ict_username = input("ict_username: ")
        ict_password = getpass.getpass("ict_password: ")

        try:
            username = driver.find_element(By.CSS_SELECTOR, "#username.input-box")
            username.send_keys(ict_username)
            password = driver.find_element(By.CSS_SELECTOR, "#password.input-box")
            password.send_keys(ict_password)

            btn_login = driver.find_element(By.CSS_SELECTOR, "#login-account.btn-login")
            driver.execute_script("arguments[0].scrollIntoView(true);", btn_login)
            btn_login.click()
            username = driver.find_element(By.CSS_SELECTOR, "#username.value").text
            usedflow = driver.find_element(By.CSS_SELECTOR, "#used-flow.value").text
            usedtime = driver.find_element(By.CSS_SELECTOR, "#used-time.value").text
            ipv4 = driver.find_element(By.CSS_SELECTOR, "#ipv4.value").text
            print("\nLogin succeeded")

            print(f"Username: {username}")
            print(f"Used flow: {usedflow}")
            print(f"Used time: {usedtime}")
            print(f"IP address: {ipv4}")
        except BaseException as e:
            print(f"Login Internal error: {e}")

    finally:
        driver.quit()
