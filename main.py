import undetected_chromedriver as uc
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
user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
options = Options()
options.add_argument(f'user-agent={user_agent}')
options.add_argument("--disable-blink-features=AutomationControlled")
chromedriver_path = ChromeDriverManager().install()
service = Service(executable_path=chromedriver_path)
driver = uc.Chrome(options=options, use_subprocess=True)
try:
    driver.get("https://mobile.de")

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
    consent_button = WebDriverWait(driver, 3000).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.mde-consent-accept-btn"))
    )
    consent_button.click()

    try:
        honda = driver.find_element(By.XPATH, "//option[@value='11000']")
        honda.click()
    except Exception as e:
        print("Honda input not found, continuing...")
    time.sleep(2)
    try:
        s2000 = driver.find_element(By.XPATH, "//option[@value='18']")
        s2000.click()
    except Exception as e:
        print("s2000 input not found, continuing...")
    time.sleep(2)
    price = driver.find_element(By.XPATH, "//option[@value='27500']")
    price.click()
    time.sleep(2)
    try:
        search_button = driver.find_element(By.XPATH, "//button[@data-testid='qs-submit-button']")
        search_button.click()
    except Exception as e:
        print("Search button not found, continuing...")
    time.sleep(3) 


    # # Wait for search results to update after sorting and filtering
    results = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, "//article[@class='A3G6X vTKPY' and not(@data-testid)]")) # Or a more specific selector for results
    )
    print(results)
    #
    print(f"Found {len(results)} results after sorting and filtering.")

    # Extract and print car information (optional, can be re-enabled)
    for result in results[1:]:
        try:
            title = result.find_element(By.CLASS_NAME, "headline-block").text
            price = result.find_element(By.CLASS_NAME, "price-block").text
            print(f"Title: {title}, Price: {price}")
        except Exception as e:
            print("Could not extract details for one of the results:", e)

    time.sleep(5000)
except Exception as e:
    print("An error occurred:", e)

# finally:
#     driver.quit()
