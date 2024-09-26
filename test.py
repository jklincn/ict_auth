from pathlib import Path
import json

from selenium import webdriver

path = Path.home() / ".local/ict_auth"

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
driver.set_page_load_timeout(5)

try:
    driver.get("https://jklincn.com/")
    print(f"Test passed")
except BaseException as e:
    print(f"Page load timed out")
    exit(-1)

driver.quit()