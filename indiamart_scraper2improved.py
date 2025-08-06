import pandas as pd
import random
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ----------------------------------------
# 🔁 User-Agent Rotation List
# ----------------------------------------
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/116 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/114 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/103 Safari/537.36",
]

# ----------------------------------------
# 🌐 Optional Proxy Setup
# ----------------------------------------
proxy = None  # Example: "username:password@123.45.67.89:8080"

# ----------------------------------------
# 🚀 Create WebDriver
# ----------------------------------------
def get_driver():
    user_agent = random.choice(USER_AGENTS)
    print(f"🧠 Using User-Agent: {user_agent}")

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--window-size=1280,720")
    chrome_options.add_argument(f"--user-agent={user_agent}")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    # Uncomment below to run headless (no browser pops up)
    # chrome_options.add_argument("--headless=new")

    if proxy:
        chrome_options.add_argument(f'--proxy-server=http://{proxy}')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

# ----------------------------------------
# 🔍 Find Search Box
# ----------------------------------------
def find_search_box(driver):
    wait = WebDriverWait(driver, 15)
    selectors = [
        (By.NAME, "ss"),
        (By.ID, "search-text"),
        (By.CSS_SELECTOR, "input[placeholder*='Search']"),
        (By.CSS_SELECTOR, "input[type='text']")
    ]
    for by, value in selectors:
        try:
            element = wait.until(EC.presence_of_element_located((by, value)))
            if element.is_displayed():
                return element
        except:
            continue
    raise Exception("❌ Search box not found.")

# ----------------------------------------
# ❌ Close Any Popups
# ----------------------------------------
def close_popups(driver):
    popup_selectors = [".popupCloseButton", ".mfp-close", ".MuiDialog-root button"]
    for selector in popup_selectors:
        try:
            popup_btn = driver.find_element(By.CSS_SELECTOR, selector)
            if popup_btn.is_displayed():
                popup_btn.click()
                time.sleep(1)
                break
        except:
            continue

# ----------------------------------------
# 🧪 Load Chemical Names
# ----------------------------------------
try:
    df_input = pd.read_csv("input_chemicals.csv", encoding='utf-8')
    if "Chemical" not in df_input.columns:
        raise ValueError("Column 'Chemical' not found in the CSV.")
    chemicals = df_input["Chemical"].dropna().unique().tolist()
except Exception as e:
    print(f"❌ Problem reading 'input_chemicals.csv': {e}")
    exit()

results = []

# ----------------------------------------
# ✅ Main Scraping Logic
# ----------------------------------------
try:
    driver = get_driver()
    wait = WebDriverWait(driver, 15)
except Exception as e:
    print(f"❌ Failed to initialize WebDriver: {e}")
    exit()

for chemical in chemicals:
    print(f"\n🔍 Searching: {chemical}")
    try:
        driver.get("https://www.indiamart.com/")
        close_popups(driver)

        try:
            search_box = find_search_box(driver)
        except Exception as e:
            print(f"❌ Unable to find search box: {e}")
            continue

        search_box.clear()
        search_box.send_keys(chemical)
        search_box.send_keys(Keys.RETURN)

        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.card.brs5")))
        except:
            print(f"❌ No product cards found for '{chemical}'")
            continue

        cards = driver.find_elements(By.CSS_SELECTOR, "div.card.brs5")

        if not cards:
            print(f"❌ No products found for '{chemical}'")
            continue

        for card in cards[:10]:
            try:
                product_name = card.find_element(By.CSS_SELECTOR, ".producttitle a").text.strip()
                company_name = card.find_element(By.CSS_SELECTOR, ".companyname a").text.strip()

                try:
                    price = card.find_element(By.CSS_SELECTOR, ".price").text.strip()
                except:
                    price = "Not listed"

                try:
                    location = card.find_element(By.CSS_SELECTOR, ".newLocationUi p").text.strip()
                except:
                    location = "Not listed"

                try:
                    phone_el = card.find_element(By.CSS_SELECTOR, ".pns_h, .viewn")
                    phone = phone_el.text.strip().replace("Call", "").replace("View Mobile Number", "").strip()
                except:
                    phone = "Not available"

                results.append({
                    "Chemical": chemical,
                    "Product Name": product_name,
                    "Company": company_name,
                    "Location": location,
                    "Price": price,
                    "Phone": phone
                })

                print(f"✅ Scraped: {product_name[:60]}...")

            except Exception as e:
                print(f"⚠️ Skipped a card block: {e}")

        # Random delay to mimic human behavior
        time.sleep(random.uniform(2, 5))

    except Exception as e:
        print(f"❌ Error while processing '{chemical}': {e}")
        try:
            driver.save_screenshot("error_screenshot.png")
        except:
            pass

# -----------------------------
# 💾 Save Results to CSV
# -----------------------------
if results:
    try:
        df_out = pd.DataFrame(results)
        df_out.to_csv("indiamart_chemical_results.csv", index=False, encoding='utf-8-sig')
        print("\n✅ Scraping complete! Saved to 'indiamart_chemical_results.csv'")
    except Exception as e:
        print(f"❌ Error writing CSV file: {e}")
else:
    print("⚠️ No data was scraped.")

# ✅ All done!
driver.quit()