# debug_manual.py

from auth import ensure_valid_login
from utils import get_driver

print("🚀 Starting Manual Debug Mode...")

# Get a browser and log in using your cookies
driver = get_driver()
ensure_valid_login(driver)

print("\n\n✅ OKAY, BROWSER IS READY FOR YOU!")
print("--------------------------------------------------")
print("The browser window is now logged into IndiaMART.")
print("Please DO NOT close it yet.")
print("Follow the manual steps I gave you to inspect the page.")
print("--------------------------------------------------")

# This line will keep the browser open until you press ENTER
input("\n\n👉 After you have finished your inspection, press ENTER in this terminal to close the browser.")

driver.quit()
print("\n✅ Debug session finished.")