import pickle
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# -------------------------------
# 🔐 Load Login Cookies
# -------------------------------
def load_cookies(driver):
    try:
        with open("indiamart_cookies.pkl", "rb") as f:
            cookies = pickle.load(f)
        for cookie in cookies:
            driver.add_cookie(cookie)
        print("✅ Cookies loaded successfully.")
    except Exception as e:
        print(f"❌ Cookie loading failed: {e}")

# -------------------------------
# 🚗 Initialize Selenium Driver
# -------------------------------
def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1280,720")
    # Optional headless: comment out if you want browser visible
    # options.add_argument("--headless=new")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.set_page_load_timeout(30)
    return driver

# -------------------------------
# ✖ Close Popups (Login, Promo etc.)
# -------------------------------
def dismiss_popups(driver):
    try:
        popup = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".popupCloseButton, .mfp-close"))
        )
        driver.execute_script("arguments[0].click();", popup)
        print("🔕 Closed popup.")
        time.sleep(1)
    except:
        pass

# -------------------------------
# 📞 Reveal actual phone number
# -------------------------------
def get_phone_number(driver, card):
    try:
        view_btn = card.find_element(By.CSS_SELECTOR, ".pns_h, .viewn")
        driver.execute_script("arguments[0].scrollIntoView(true);", view_btn)
        time.sleep(1)

        driver.execute_script("arguments[0].click();", view_btn)
        time.sleep(3)

        phone_el = card.find_element(By.CSS_SELECTOR, ".pns_h, .viewn")
        phone = phone_el.text.strip().replace("View Mobile Number", "").replace("Call", "").strip()

        if phone and ("+" in phone or phone.replace("-", "").strip().isdigit()):
            return phone
        return "Still hidden after click"
    except Exception as e:
        print(f"❌ Error revealing phone: {e}")
        return "Not available"

# -------------------------------
# 🚀 Main Scraper Logic
# -------------------------------
def run_scraper():
    try:
        df = pd.read_csv("input_chemicals.csv")
        chemicals = df["Chemical"].dropna().unique().tolist()
    except Exception as e:
        print(f"❌ Error reading input CSV: {e}")
        return

    results = []
    driver = get_driver()
    driver.get("https://www.indiamart.com/")
    time.sleep(2)
    load_cookies(driver)
    print("🔄 Refreshing after loading cookies...\n")
    driver.refresh()
    time.sleep(3)

    for chemical in chemicals:
        print(f"\n🔍 Searching: {chemical}")
        try:
            search_url = f"https://dir.indiamart.com/search.mp?ss={chemical.replace(' ', '+')}"
            driver.get(search_url)
            time.sleep(4)
            dismiss_popups(driver)

            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.card.brs5"))
            )

            cards = driver.find_elements(By.CSS_SELECTOR, "div.card.brs5")
            if not cards:
                print(f"⚠️ No products found for {chemical}")
                continue

            for card in cards[:10]:
                try:
                    product_name = card.find_element(By.CSS_SELECTOR, ".producttitle a").text.strip()
                    company = card.find_element(By.CSS_SELECTOR, ".companyname a").text.strip()
                    location = card.find_element(By.CSS_SELECTOR, ".newLocationUi p").text.strip() if card.find_elements(By.CSS_SELECTOR, ".newLocationUi p") else "Not listed"
                    price = card.find_element(By.CSS_SELECTOR, ".price").text.strip() if card.find_elements(By.CSS_SELECTOR, ".price") else "Not listed"
                    phone = get_phone_number(driver, card)

                    results.append({
                        "Chemical": chemical,
                        "Product Name": product_name,
                        "Company": company,
                        "Location": location,
                        "Price": price,
                        "Phone": phone,
                    })

                    print(f"✅ {product_name[:60]}... | 🏢 {company} | 📞 {phone}")

                except Exception as e:
                    print(f"⚠️ Skipped a card: {e}")

            time.sleep(6)  # 🙋 Human-like delay

        except Exception as e:
            print(f"❌ Error for {chemical}: {e}")
            continue

    driver.quit()

    if results:
        df_out = pd.DataFrame(results)
        df_out.to_csv("indiamart_scrape_with_phone.csv", index=False, encoding='utf-8-sig')
        print("\n✅ Saved to 'indiamart_scrape_with_phone.csv'")
    else:
        print("⚠️ No results saved.")

# --------------------------------------
# ▶️ Run It
# --------------------------------------
if __name__ == "__main__":
    run_scraper()