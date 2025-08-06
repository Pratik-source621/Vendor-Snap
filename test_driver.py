from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# Set Chrome options
options = Options()
# Keep headless OFF for now so you can see the browser
# options.add_argument("--headless")

# Set the path to your downloaded ChromeDriver
service = Service("/Users/pratikbharuka/Documents/chromedriver")

# Launch the browser
driver = webdriver.Chrome(service=service, options=options)

# Open Google
driver.get("https://www.google.com")

# Keep the browser open until you hit Enter in terminal
input("✅ Press Enter to close the browser...")

# Close the browser
driver.quit()
