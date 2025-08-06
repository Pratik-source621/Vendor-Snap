# india_mart_scraper.py

import pandas as pd
import random
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ----------------------------------------
# 🔁 User-Agent List (Rotate these)
# ----------------------------------------
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/116 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/114 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/103 Safari/537.36",
]

# ----------------------------------------
# 🌐 Optional Proxy Setup (change this)
# Format: "ip:port" or "username:password@ip:port"
# Example proxy = "123.456.789.000:3128"
# ----------------------------------------
proxy = None  # ← Add your proxy IP here if needed
# Example: proxy = "username:password@123.45.67.89:8080"

# ----------------------------------------
# 🚀 Setup WebDriver with Proxy & UA
# ----------------------------------------
def get_driver():
    user_agent = random.choice(USER_AGENTS)
    print(f"🧠 Using User-Agent: {user_agent}")

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--window-size=1280,720")
    chrome_options.add_argument(f"user-agent={user_agent}")

    if proxy:
        chrome_options.add_argument(f'--proxy-server=http://{proxy}')

    return webdriver.Chrome(options=chrome_options)

# ----------------------------------------
# 🔍 Search Box Fallback Logic
# ----------------------------------------
def find_search_box(driver):
    wait = WebDriverWait(driver, 15)
    candidates = [
        (By.NAME, "ss"),
        (By.ID, "search-text"),
        (By.CSS_SELECTOR, "input[placeholder*='Search']"),
        (By.CSS_SELECTOR, "input[type='text']"),
    ]
    for by, value in candidates:
        try:
            element = wait.until(EC.presence_of_element_located((by, value)))
            if element.is_displayed():
                return element
        except:
            continue
    raise Exception("❌ Search box not found")

# ----------------------------------------
# 🧪 Load Chemical List from Excel
# ----------------------------------------
df_input = pd.read_excel("input_chemicals.xlsx", engine='openpyxl')
chemicals = df_input["Chemical"].dropna().unique().tolist()

# ----------------------------------------
# 💬 Start Scraping
# ----------------------------------------
results = []

try:
    driver = get_driver()
    wait = WebDriverWait(driver, 15)

    for chemical in chemicals:
        print(f"\n🔍 Searching: {chemical}")
        try:
            driver.get("https://www.indiamart.com/")

            search_box = find_search_box(driver)
            search_box.clear()
            search_box.send_keys(chemical)
            search_box.send_keys(Keys.RETURN)

            # Wait for cards
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.card.brs5")))
            cards = driver.find_elements(By.CSS_SELECTOR, "div.card.brs5")

            if not cards:
                print(f"❌ No products found for: {chemical}")
                continue

            for card in cards[:10]:  # Limit per chemical
                try:
                    product_name = card.find_element(By.CSS_SELECTOR, ".producttitle a").text.strip()
                    company_name = card.find_element(By.CSS_SELECTOR, ".companyname a").text.strip()
                    price = card.find_element(By.CSS_SELECTOR, ".price").text.strip()

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
                    print(f"⚠️ Skipped a product block: {e}")

        except Exception as e:
            print(f"⚠️ Error for '{chemical}': {e}")
            try:
                driver.save_screenshot("error_screenshot.png")
            except:
                pass

finally:
    driver.quit()

# ----------------------------------------
# 💾 Save to Excel
# ----------------------------------------
if results:
    df = pd.DataFrame(results)
    df.to_excel("indiamart_chemical_results.xlsx", index=False)
    print("\n✅ Scrape Complete → Saved to 'indiamart_chemical_results.xlsx'")
else:
    print("⚠️ No data scraped.")
# This script scrapes product information from IndiaMART for specified chemical queries
# and saves the results to an Excel file named output.xlsx.
# Make sure to install the required packages before running:
# pip install selenium pandas openpyxl webdriver-manager
# Note: Ensure you have the correct version of ChromeDriver that matches your Chrome browser version.
# You can run this script in a Python environment with the necessary packages installed.
# The script uses Selenium to automate the browser and scrape data from the IndiaMART website.
# Adjust the queries list to include any other chemicals you want to search for.
# The script is designed to run headless, but you can comment out the headless option
# if you want to see the browser in action while scraping.
# The script limits the results to the top 10 products for each query to avoid excessive data
# and to keep the output manageable. You can adjust this limit as needed.   

