import pickle
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Step 1: Launch browser
options = webdriver.ChromeOptions()
options.add_argument("--window-size=1280,720")
# ✅ DO NOT use headless mode so you can log in manually

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Step 2: Open IndiaMART page
driver.get("https://www.indiamart.com/")

print("\n🚀 Please log in manually using your phone number.")
print("📲 Wait for OTP, submit it, make sure you're successfully logged in.")
print("✅ After login is complete, come back here and press Enter.")

input("🔒 Press Enter after you're logged in → ")

# Step 3: Save cookies
cookies = driver.get_cookies()

with open("indiamart_cookies.pkl", "wb") as f:
    pickle.dump(cookies, f)

print("✅ Login cookies saved to 'indiamart_cookies.pkl'")

# Optional: Keep browser open for testing
time.sleep(3)
driver.quit()