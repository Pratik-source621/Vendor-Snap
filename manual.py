from selenium import webdriver
import pickle
import time
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

driver.get("https://www.indiamart.com/")
time.sleep(2)

with open("indiamart_cookies.pkl", "rb") as f:
    cookies = pickle.load(f)

for cookie in cookies:
    driver.add_cookie(cookie)

driver.refresh()

input(" Do you see your profile/account menu at the top right? Press Enter to close browser...")
driver.quit()