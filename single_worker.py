# single_worker.py (FINAL - Multi-Attack & Smart Button/Scroll Version)

import time
import traceback
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from auth import ensure_valid_login
from utils import get_driver, close_global_popups, detect_and_avoid_captcha, get_phone_number

def scrape_group(chemicals, target_results_per_item=10):
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
            
            # --- Search and Submit Logic (Your original multi-attack) ---
            search_box = wait.until(EC.presence_of_element_located((By.ID, "search_string")))
            search_box.clear()
            search_box.send_keys(chemical)
            time.sleep(1.5)
            search_box.send_keys(Keys.RETURN)
            print("  -> Attempt 1: Pressed ENTER.")
            
            try:
                WebDriverWait(driver, 5).until(EC.number_of_windows_to_be(2))
                print("  -> Success! New tab opened.")
            except TimeoutException:
                print("  -> Attempt 2: ENTER failed, trying to click popup button.")
                try:
                    popup_search_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Search']")))
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
            
            ## >> NEW & IMPROVED "SMART SCROLL" LOGIC <<
            print(f"  -> Loading results to reach target of ~{target_results_per_item}...")
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.card.brs5, .noResults")))
            
            while True:
                cards = driver.find_elements(By.CSS_SELECTOR, "div.card.brs5")
                print(f"  -> Found {len(cards)} cards so far...")

                if len(cards) >= target_results_per_item:
                    print(f"  -> Target of {target_results_per_item} results reached.")
                    break
                
                # Method 1: Try to click the "Show More Results" button (most reliable)
                try:
                    # Use a short wait to quickly check if the button exists
                    show_more_button = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable((By.ID, "loadMore"))
                    )
                    driver.execute_script("arguments[0].scrollIntoView(true);", show_more_button)
                    time.sleep(0.5)
                    show_more_button.click()
                    print("  -> Clicked 'Show More Results' button.")
                    time.sleep(3) # Wait for new results to load
                    continue # Restart the loop to re-count cards
                except TimeoutException:
                    # Button not found, fall back to scrolling
                    pass

                # Method 2: Fallback to infinite scrolling
                last_height = driver.execute_script("return document.body.scrollHeight")
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                new_height = driver.execute_script("return document.body.scrollHeight")

                if new_height == last_height:
                    print("  -> Reached end of page. No more results found.")
                    break # Exit loop if scroll height doesn't change
            ## >> END OF NEW LOGIC <<

            # --- Scrape the Data ---
            all_cards = driver.find_elements(By.CSS_SELECTOR, "div.card.brs5")
            if not all_cards:
                print(f"⚠️ No product cards found for '{chemical}'.")
            else:
                print(f"  -> Processing the top {min(len(all_cards), target_results_per_item)} results...")
                for card in all_cards[:target_results_per_item]:
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
                        print(f"    ✅ {product[:50]}... [📞 {phone}]")
                    except Exception as e:
                        print(f"    ⚠️ Error parsing a card: {e}")
            
            # --- Cleanup ---
            driver.close()
            driver.switch_to.window(original_window)

        except Exception:
            print(f"❌ A critical error occurred for '{chemical}':")
            print(traceback.format_exc())
            for handle in driver.window_handles:
                if handle != original_window:
                    driver.switch_to.window(handle)
                    driver.close()
            driver.switch_to.window(original_window)
            continue

    driver.quit()
    return results