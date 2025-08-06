import pandas as pd
import random
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ------------------------------------------------------------------------------
# 🔁 USER AGENTS
# ------------------------------------------------------------------------------
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
    "Mozilla/5.0 (X11; Linux x86_64)...",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
]

# ------------------------------------------------------------------------------
# 📂 Logging Setup
# ------------------------------------------------------------------------------
log_lines = []
def log(msg):
    print(msg)
    log_lines.append(msg)

def save_log():
    with open("scrape_log.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines))

# ------------------------------------------------------------------------------
# 📥 PROXY FETCH + TESTER
# ------------------------------------------------------------------------------
def fetch_proxies(limit=20):
    try:
        url = "https://www.proxy-list.download/api/v1/get?type=http"
        response = requests.get(url, timeout=10)
        proxies = response.text.strip().split("\r\n")
        log(f"🔁 Fetched {len(proxies[:limit])} fresh proxies.")
        return proxies[:limit]
    except Exception as e:
        log(f"❌ Failed to fetch proxies: {e}")
        return []

def test_proxy(proxy):
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument(f"--proxy-server=http://{proxy}")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.set_page_load_timeout(10)
        driver.get("https://httpbin.org/ip")
        driver.quit()
        return True
    except:
        try:
            driver.quit()
        except:
            pass
        return False

def export_proxy_lists(working, dead):
    with open("working_proxies.txt", "w") as wf:
        wf.write("\n".join(working))
    with open("dead_proxies.txt", "w") as df:
        df.write("\n".join(dead))
    log("✅ Proxy test results saved to 'working_proxies.txt' and 'dead_proxies.txt'.")

# ------------------------------------------------------------------------------
# ♻️ REAL-TIME PROXY POOL
# ------------------------------------------------------------------------------
class ProxyPool:
    def __init__(self):
        self.working = []
        self.dead = []
        self.refill()

    def refill(self):
        raw = fetch_proxies(30)
        self.working.clear()
        self.dead.clear()
        for ip in raw:
            if test_proxy(ip):
                self.working.append(ip)
                log(f"✅ Proxy OK: {ip}")
            else:
                self.dead.append(ip)
                log(f"❌ Proxy Dead: {ip}")
        export_proxy_lists(self.working, self.dead)

    def get_proxy(self):
        if not self.working:
            log("♻️ No usable proxies. Rechecking...")
            self.refill()
        return random.choice(self.working)

    def discard_proxy(self, proxy):
        if proxy in self.working:
            self.working.remove(proxy)
            self.dead.append(proxy)
            log(f"🗑️ Removed proxy: {proxy}")
        export_proxy_lists(self.working, self.dead)

# ------------------------------------------------------------------------------
# 🚗 GET DRIVER
# ------------------------------------------------------------------------------
def get_driver(proxy_pool):
    ua = random.choice(USER_AGENTS)
    proxy = proxy_pool.get_proxy()
    log(f"\n🧠 UA: {ua}")
    log(f"🌐 Proxy: {proxy}")

    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1280,720")
    options.add_argument(f"--user-agent={ua}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_argument("--headless=new")
    options.add_argument(f"--proxy-server=http://{proxy}")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.set_page_load_timeout(15)
    return driver, proxy

# ------------------------------------------------------------------------------
# 🚧 OTHER UTILITIES
# ------------------------------------------------------------------------------
def find_search_box(driver):
    wait = WebDriverWait(driver, 15)
    selectors = [
        (By.NAME, "ss"),
        (By.ID, "search-text"),
        (By.CSS_SELECTOR, "input[placeholder*='Search']"),
        (By.CSS_SELECTOR, "input[type='text']"),
    ]
    for by, val in selectors:
        try:
            el = wait.until(EC.presence_of_element_located((by, val)))
            if el.is_displayed():
                return el
        except:
            continue
    raise Exception("❌ Search box not found.")

def close_popups(driver):
    for sel in [".popupCloseButton", ".mfp-close", ".MuiDialog-root button"]:
        try:
            btn = driver.find_element(By.CSS_SELECTOR, sel)
            if btn.is_displayed():
                btn.click()
                time.sleep(1)
        except:
            continue

def is_captcha(driver):
    try:
        return "captcha" in driver.page_source.lower()
    except:
        return False

# ------------------------------------------------------------------------------
# 🧪 LOAD INPUT FILE
# ------------------------------------------------------------------------------
try:
    df_input = pd.read_csv("input_chemicals.csv")
    if "Chemical" not in df_input.columns:
        raise Exception("Missing column: 'Chemical'")
    chemicals = df_input["Chemical"].dropna().unique().tolist()
except Exception as e:
    log(f"❌ Failed to load input: {e}")
    save_log()
    exit()

# ------------------------------------------------------------------------------
# 🔍 SCRAPING BEGINS
# ------------------------------------------------------------------------------
results, MAX_RETRIES = [], 3
proxy_pool = ProxyPool()

for chemical in chemicals:
    log(f"\n🔍 Searching: {chemical}")

    for attempt in range(1, MAX_RETRIES + 1):
        driver, proxy = None, None
        try:
            driver, proxy = get_driver(proxy_pool)
            wait = WebDriverWait(driver, 15)
            driver.get("https://www.indiamart.com/")
            close_popups(driver)

            if is_captcha(driver):
                log(f"🛑 CAPTCHA for: {chemical}")
                proxy_pool.discard_proxy(proxy)
                driver.quit()
                break

            search_box = find_search_box(driver)
            search_box.clear()
            search_box.send_keys(chemical)
            search_box.send_keys(Keys.RETURN)

            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.card.brs5")))
            cards = driver.find_elements(By.CSS_SELECTOR, "div.card.brs5")

            if not cards:
                log(f"⚠️ No results for {chemical}")
                proxy_pool.discard_proxy(proxy)
                driver.quit()
                break

            for card in cards[:10]:
                try:
                    product_name = card.find_element(By.CSS_SELECTOR, ".producttitle a").text.strip()
                    company_name = card.find_element(By.CSS_SELECTOR, ".companyname a").text.strip()
                    price = card.find_element(By.CSS_SELECTOR, ".price").text.strip() if card.find_elements(By.CSS_SELECTOR, ".price") else "Not listed"
                    location = card.find_element(By.CSS_SELECTOR, ".newLocationUi p").text.strip() if card.find_elements(By.CSS_SELECTOR, ".newLocationUi p") else "Not listed"
                    phone = card.find_element(By.CSS_SELECTOR, ".pns_h, .viewn").text.strip().replace("Call", "").replace("View Mobile Number", "").strip() if card.find_elements(By.CSS_SELECTOR, ".pns_h, .viewn") else "Not available"

                    results.append({
                        "Chemical": chemical,
                        "Product Name": product_name,
                        "Company": company_name,
                        "Location": location,
                        "Price": price,
                        "Phone": phone
                    })

                    log(f"✅ {product_name[:60]}")

                except Exception as e:
                    log(f"⚠️ Error parsing card: {e}")

            driver.quit()
            pd.DataFrame(results).to_csv("indiamart_results_temp.csv", index=False, encoding='utf-8-sig')
            break

        except Exception as e:
            log(f"❌ {attempt=}, {chemical=} → {e}")
            if proxy:
                proxy_pool.discard_proxy(proxy)
        finally:
            try: driver.quit()
            except: pass
        time.sleep(random.uniform(3, 6))

# ------------------------------------------------------------------------------
# 💾 SAVE RESULTS
# ------------------------------------------------------------------------------
if results:
    try:
        df = pd.DataFrame(results)
        df.to_csv("indiamart_chemical_results.csv", index=False, encoding='utf-8-sig')
        log("✅ Saved to: indiamart_chemical_results.csv")
    except Exception as e:
        log(f"❌ Save error: {e}")
else:
    log("⚠️ No data scraped.")

# 🔚 Save final log
save_log()
log("📝 Log written to scrape_log.txt")