# utils.py

import time, random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    "Mozilla/5.0 (X11; Linux x86_64)...",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)..."
]

def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")
    options.add_argument("--window-size=1280x800")
    options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_argument("--headless=new")  # Uncomment for silent run
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def close_global_popups(driver):
    for selector in [".popupCloseButton", ".mfp-close"]:
        try:
            driver.find_element(By.CSS_SELECTOR, selector).click()
            time.sleep(0.5)
        except:
            continue

def detect_and_avoid_captcha(driver):
    if "captcha" in driver.page_source.lower() or "verify" in driver.page_source.lower():
        input("⚠️ CAPTCHA detected! Solve it manually, then press ENTER...")
        return True
    return False

def get_phone_number(driver, card):
    try:
        view_btn = card.find_element(By.CSS_SELECTOR, ".viewn")
        driver.execute_script("arguments[0].click();", view_btn)
        WebDriverWait(card, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".pns_h")))
        phone = card.find_element(By.CSS_SELECTOR, ".pns_h").text.strip()
        return phone or "Not available"
    except:
        return "Not available"