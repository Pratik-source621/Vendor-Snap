# single_worker.py (FINAL - Multi-Attack Version)

import time
import traceback
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException # Import this
from auth import ensure_valid_login
from utils import get_driver, close_global_popups, detect_and_avoid_captcha, get_phone_number

def scrape_group(chemicals):
    results = []
    driver = get_driver()
    ensure_valid_login(driver)
    original_window = driver.current_window_handle

    for chemical in chemicals:
        print(f"\n🔍 Searching: {chemical}")
        
        try:
            # --- Always reset to a clean state ---
            driver.switch_to.window(original_window)
            driver.get("https://buyer.indiamart.com/")
            time.sleep(2)
            close_global_popups(driver)

            if detect_and_avoid_captcha(driver):
                continue

            wait = WebDriverWait(driver, 10)
            
            # --- Search and Submit Logic ---
            search_box = wait.until(EC.presence_of_element_located((By.ID, "search_string")))
            search_box.clear()
            search_box.send_keys(chemical)
            time.sleep(1.5)

            # --- MULTI-STEP ATTACK TO SUBMIT SEARCH ---
            # Attack 1: Try pressing ENTER first (most reliable)
            search_box.send_keys(Keys.RETURN)
            print("  -> Attempt 1: Pressed ENTER.")
            
            try:
                # Check if the results page loaded after pressing ENTER
                WebDriverWait(driver, 5).until(EC.number_of_windows_to_be(2))
                print("  -> Success! New tab opened.")
            except TimeoutException:
                # If ENTER didn't work, a new tab didn't open. So, try clicking the button.
                print("  -> Attempt 2: ENTER failed, trying to click popup button.")
                try:
                    popup_search_button = wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Search']"))
                    )
                    driver.execute_script("arguments[0].click();", popup_search_button)
                    WebDriverWait(driver, 5).until(EC.number_of_windows_to_be(2))
                    print("  -> Success! Clicked popup button.")
                except Exception as e:
                    screenshot_path = f"errors/{chemical.replace(' ', '_')}_final_fail.png"
                    driver.save_screenshot(screenshot_path)
                    print(f"  -> FINAL ATTEMPT FAILED. Could not submit search for '{chemical}'. Skipping. Error: {e}")
                    continue

            # --- Handle the New Tab ---
            new_window = [window for window in driver.window_handles if window != original_window][0]
            driver.switch_to.window(new_window)
            time.sleep(2)

            # --- Scrape the Data ---
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.card.brs5, .noResults")))
            
            cards = driver.find_elements(By.CSS_SELECTOR, "div.card.brs5")
            if not cards:
                print(f"⚠️ No product cards found for '{chemical}'.")
            else:
                for card in cards[:10]:
                    try:
                        product = card.find_element(By.CSS_SELECTOR, ".producttitle a").text.strip()
                        company = card.find_element(By.CSS_SELECTOR, ".companyname a").text.strip()
                        price = card.find_element(By.CSS_SELECTOR, ".price").text.strip() if card.find_elements(By.CSS_SELECTOR, ".price") else "Not listed"
                        location = card.find_element(By.CSS_SELECTOR, ".newLocationUi p").text.strip() if card.find_elements(By.CSS_SELECTOR, ".newLocationUi p") else "Not listed"
                        phone = get_phone_number(driver, card)

                        results.append({
                            "Chemical": chemical, "Product Name": product, "Company": company,
                            "Location": location, "Price": price, "Phone": phone
                        })
                        print(f"✅ {product[:60]}... [📞 {phone}]")
                    except Exception as e:
                        print(f"⚠️ Error parsing a card: {e}")
            
            # --- Cleanup ---
            driver.close()
            driver.switch_to.window(original_window)

        except Exception:
            print(f"❌ A critical error occurred for '{chemical}':")
            print(traceback.format_exc())
            # Cleanup routine
            for handle in driver.window_handles:
                if handle != original_window:
                    driver.switch_to.window(handle)
                    driver.close()
            driver.switch_to.window(original_window)
            continue

    driver.quit()
    return results