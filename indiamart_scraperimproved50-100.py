import pandas as pd
import random
import time
import traceback

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ----------------------------------------
# 🎯 CONFIGURATION
# ----------------------------------------
MAX_RETRIES = 2
DELAY_RANGE = (8, 15)  # ⏳ Slow & steady
MAX_CARDS = 10  # 🛑 Limit products per chemical

# ----------------------------------------
# ✨ User-Agent Rotation
# ----------------------------------------
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
    "Mozilla/5.0 (X11; Linux x86_64)...",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)..."
]

# ----------------------------------------
# 🚗 Get Chrome Driver (NO PROXY)
# ----------------------------------------
def get_driver():
    ua = random.choice(USER_AGENTS)
    print(f"🧠 Using User-Agent: {ua}")
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1280,720")
    options.add_argument(f"user-agent={ua}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_argument("--headless=new")  # Optional

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.set_page_load_timeout(30)
    return driver

# ----------------------------------------
# 💡 Utility: Find Search Box
# ----------------------------------------
def find_search_box(driver):
    wait = WebDriverWait(driver, 15)
    selectors = [(By.NAME, "ss"), (By.ID, "search-text"),
                 (By.CSS_SELECTOR, "input[placeholder*='Search']"),
                 (By.CSS_SELECTOR, "input[type='text']")]
    for by, val in selectors:
        try:
            box = wait.until(EC.presence_of_element_located((by, val)))
            if box.is_displayed():
                return box
        except:
            continue
    raise Exception("❌ Search box not found")

# ----------------------------------------
# 💡 Utility: Close IndiaMART Popups
# ----------------------------------------
def close_popups(driver):
    for selector in [".popupCloseButton", ".mfp-close"]:
        try:
            btn = driver.find_element(By.CSS_SELECTOR, selector)
            if btn.is_displayed():
                btn.click()
                time.sleep(1)
        except:
            continue

# ----------------------------------------
# 📥 Load Input CSV
# ----------------------------------------
try:
    df_input = pd.read_csv("input_chemicals.csv")
    if "Chemical" not in df_input.columns:
        raise Exception("Missing 'Chemical' column in CSV.")
    chemicals = df_input["Chemical"].dropna().unique().tolist()
except Exception as e:
    print(f"❌ Input File Error: {e}")
    exit()

# ----------------------------------------
# 🧪 Start Scraping
# ----------------------------------------
results = []

for chemical in chemicals:
    print(f"\n🔍 Searching: {chemical}")

    for attempt in range(1, MAX_RETRIES + 1):
        driver = None
        try:
            driver = get_driver()
            wait = WebDriverWait(driver, 15)
            driver.get("https://www.indiamart.com/")
            close_popups(driver)

            search_box = find_search_box(driver)
            search_box.clear()
            search_box.send_keys(chemical)
            search_box.send_keys(Keys.RETURN)

            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.card.brs5")))
            cards = driver.find_elements(By.CSS_SELECTOR, "div.card.brs5")

            if not cards:
                print(f"⚠️ No products found for '{chemical}'")
                break

            for card in cards[:MAX_CARDS]:
                try:
                    product_name = card.find_element(By.CSS_SELECTOR, ".producttitle a").text.strip()
                    company = card.find_element(By.CSS_SELECTOR, ".companyname a").text.strip()
                    price = card.find_element(By.CSS_SELECTOR, ".price").text.strip() if card.find_elements(By.CSS_SELECTOR, ".price") else "Not listed"
                    location = card.find_element(By.CSS_SELECTOR, ".newLocationUi p").text.strip() if card.find_elements(By.CSS_SELECTOR, ".newLocationUi p") else "Not listed"
                    phone = card.find_element(By.CSS_SELECTOR, ".pns_h, .viewn").text.strip().replace("Call", "").replace("View Mobile Number", "").strip() if card.find_elements(By.CSS_SELECTOR, ".pns_h, .viewn") else "Not available"

                    results.append({
                        "Chemical": chemical, "Product Name": product_name,
                        "Company": company, "Location": location,
                        "Price": price, "Phone": phone
                    })

                    print(f"✅ {product_name[:60]}...")
                except:
                    print("⚠️ Card skipped due to structure change")

            break  # Success — go to next chemical

        except Exception as e:
            print(f"❌ Error attempt {attempt} for '{chemical}': {e}")
            traceback.print_exc()
        finally:
            try: driver.quit()
            except: pass

        time.sleep(random.uniform(DELAY_RANGE[0], DELAY_RANGE[1]))  # 📢 Human-like delay

# ----------------------------------------
# 💾 SAVE TO CSV
# ----------------------------------------
if results:
    df_out = pd.DataFrame(results)
    df_out.to_csv("indiamart_chemical_results2.csv", index=False, encoding='utf-8-sig')
    print("\n✅ Results saved to 'indiamart_chemical_results.csv'")
else:
    print("⚠️ No data scraped.")