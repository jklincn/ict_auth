import os
import getpass
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

if __name__ == "__main__":
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

    driver = webdriver.Chrome(options=options, service=service)

    try:
        print("============== ICT Connect ==============")
        driver.get("https://gw.ict.ac.cn")
        driver.implicitly_wait(10)
        driver.find_element(By.CSS_SELECTOR, "#logout.btn-logout")
        print("You are already logged in. Good luck!")

    except NoSuchElementException:
        ict_username = input("ict_username: ")
        ict_password = getpass.getpass("ict_password: ")

        print("Starting login...", end="")

        username = driver.find_element(By.CSS_SELECTOR, "#username.input-box")
        username.send_keys(ict_username)
        password = driver.find_element(By.CSS_SELECTOR, "#password.input-box")
        password.send_keys(ict_password)

        butten_login = driver.find_element(By.CSS_SELECTOR, "#login-account.btn-login")
        driver.execute_script("arguments[0].scrollIntoView(true);", butten_login)
        butten_login.click()
        driver.implicitly_wait(10)
        username = driver.find_element(By.CSS_SELECTOR, "#username.value").text
        usedflow = driver.find_element(By.CSS_SELECTOR, "#used-flow.value").text
        usedtime = driver.find_element(By.CSS_SELECTOR, "#used-time.value").text
        ipv4 = driver.find_element(By.CSS_SELECTOR, "#ipv4.value").text
        print("Succeed")

        print(f"Username: {username}")
        print(f"Used flow: {usedflow}")
        print(f"Used time: {usedtime}")
        print(f"IP address: {ipv4}")

    finally:
        print("=========================================")
        driver.quit()
