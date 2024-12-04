import os
import subprocess
import sys

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from ict_auth import _login, _logout, check_login, get_driver, show_debug_info


def restart_frpc():
    try:
        result = subprocess.run(
            ["sudo", "systemctl", "restart", "frpc.service"],
            check=True,
            capture_output=True,
            text=True,
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(e.stderr)
        exit(1)


if __name__ == "__main__":

    try:
        driver = get_driver()

        ict_username = os.getenv("ICT_USERNAME")
        ict_password = os.getenv("ICT_PASSWORD")

        if "--check" in sys.argv:
            if check_login(driver):
                _logout(driver)
            _login(driver, ict_username, ict_password)
            try:
                driver.find_element(By.CSS_SELECTOR, "#username.value")
                print("[INFO] Account verification successful.")

            except NoSuchElementException:
                print("[ERROR] Account verification failed.")
                print("[ERROR] You can manually logout first and then try again.")
                exit(1)
        else:
            if not check_login(driver):
                print(
                    "[INFO] Connection interruption detected. Logging in automatically."
                )

                _login(driver, ict_username, ict_password)

                username = driver.find_element(By.CSS_SELECTOR, "#username.value").text
                usedflow = driver.find_element(By.CSS_SELECTOR, "#used-flow.value").text
                usedtime = driver.find_element(By.CSS_SELECTOR, "#used-time.value").text
                ipv4 = driver.find_element(By.CSS_SELECTOR, "#ipv4.value").text
                print(f"[INFO] Username: {username}")
                print(f"[INFO] Used flow: {usedflow}")
                print(f"[INFO] Used time: {usedtime}")
                print(f"[INFO] IP address: {ipv4}")
                restart_frpc()

    except Exception:
        print(
            "\n[INTERNAL ERROR] An internal error has occurred. Please contact the developer and provide the information below."
        )
        show_debug_info()
        raise
    finally:
        driver.quit()
