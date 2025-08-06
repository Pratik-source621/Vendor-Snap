# config.py

# --- Main Configuration ---
COOKIES_FILE = "cookies.json"
INDIAMART_URL = "https://www.indiamart.com"
LOGIN_URL = "https://my.indiamart.com"
OUTPUT_FILE = "indiamart_results.csv"
COOKIE_EXPIRY_DAYS = 30

# --- Google Sheets Configuration ---
## >> THIS IS THE LINE THAT WAS MISSING <<
GOOGLE_SHEET_NAME = "IndiaMART Scraped Data" 

# --- Startup Message ---
print("✅ Config loaded:")
print(f"   - Cookies File: {COOKIES_FILE}")
print(f"   - Output CSV: {OUTPUT_FILE}")
print(f"   - Google Sheet Name: '{GOOGLE_SHEET_NAME}'")