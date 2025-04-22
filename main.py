from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import time
import os
import tempfile
from selenium import webdriver

from webdriver_manager.chrome import ChromeDriverManager

# Create a unique temporary directory with timestamp
import time
custom_data_dir = os.path.expanduser(f"/home/diogo/chrome_data_{int(time.time())}")
os.makedirs(custom_data_dir, exist_ok=True)

# Add it to your options
# Setup Chrome options
options = Options()
# options.add_argument("--remote-debugging-port=9222")
# options.add_argument("--disable-dev-shm-usage")
# options.add_argument(f"--user-data-dir={custom_data_dir}")
# options.add_argument("--disable-extensions")
# options.add_argument("--disable-gpu")
# options.add_argument("--no-sandbox")
chromedriver_path = ChromeDriverManager().install()
service = Service(executable_path=chromedriver_path)
# chrome_driver_path = os.path.expanduser("/home/diogo/chromedriver-linux64/chromedriver-linux64/chromedriver")
print('wallahi')
driver = webdriver.Chrome(service=service, options=options)
print('we made it')
try:
    driver.get("https://suchen.mobile.de/fahrzeuge/search.html")

    # Accept GDPR consent if button appears
    try:
        gdpr_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "gdpr-consent-layer-accept-all-button"))
        )
        gdpr_button.click()
        time.sleep(2)  # Allow time for the page to update
    except Exception as e:
        print("No GDPR consent popup found, continuing...")

    # # Click the search button
    search_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.ID, "dsp-upper-search-btn"))
    )
    # search_button.click()
    #
    # # Wait for search results
    # results = WebDriverWait(driver, 10).until(
    #     EC.presence_of_all_elements_located((By.CLASS_NAME, "cBox-body--resultitem"))
    # )
    #
    # print(f"Found {len(results)} results.")

    # Extract and print car information
    # for result in results:
    #     try:
    #         title = result.find_element(By.CLASS_NAME, "headline-block").text
    #         price = result.find_element(By.CLASS_NAME, "price-block").text
    #         print(f"Title: {title}, Price: {price}")
    #     except Exception as e:
    #         print("Could not extract details for one of the results:", e)

except Exception as e:
    print("An error occurred:", e)

finally:
    driver.quit()
