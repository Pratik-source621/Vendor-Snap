# auth.py

import json, os
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from config import COOKIES_FILE, INDIAMART_URL, COOKIE_EXPIRY_DAYS

def cookies_expired(path=COOKIES_FILE, max_age_days=COOKIE_EXPIRY_DAYS):
    if not os.path.exists(path): return True
    modified = datetime.fromtimestamp(os.path.getmtime(path))
    return (datetime.now() - modified).days > max_age_days

def save_cookies(driver, path=COOKIES_FILE):
    with open(path, "w") as f:
        json.dump(driver.get_cookies(), f)
    print("✅ Cookies saved.")

def load_cookies(driver, path=COOKIES_FILE):
    driver.get(INDIAMART_URL)
    with open(path, "r") as f:
        cookies = json.load(f)
    for cookie in cookies:
        for key in ["expiry", "sameSite"]:
            if key in cookie and (cookie[key] is None or cookie[key] == ''):
                del cookie[key]
        try:
            driver.add_cookie(cookie)
        except:
            continue
    driver.refresh()

def is_logged_in(driver):
    try:
        driver.get(INDIAMART_URL)
        if "Logout" in driver.page_source or "My Orders" in driver.page_source or "Hi" in driver.page_source:
            return True
        # fallback check
        driver.find_element(By.CSS_SELECTOR, ".toplogedin")
        return True
    except:
        return False

def manual_login_and_save(driver):
    print("🔐 Please log in to IndiaMART manually in the browser...")
    driver.get("https://my.indiamart.com")
    input("✅ Press ENTER after completing login...")
    save_cookies(driver)

def ensure_valid_login(driver):
    try:
        if cookies_expired():
            raise Exception("Session expired")
        load_cookies(driver)
        if not is_logged_in(driver):
            raise Exception("Login check failed")
    except Exception as e:
        print(f"📣 Re-authenticating due to: {e}")
        manual_login_and_save(driver)