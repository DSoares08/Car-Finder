import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import time

from webdriver_manager.chrome import ChromeDriverManager

# Global variables to store results
link = None
found_cars = []
prev_results = []


def setup_driver():
    """Set up and return the Chrome driver"""
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    options = Options()
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--headless")  # Run in headless mode when used by server
    chromedriver_path = ChromeDriverManager().install()
    service = Service(executable_path=chromedriver_path)
    return uc.Chrome(options=options, use_subprocess=True)


def run_search():
    """Main function to run the car search"""
    global link, found_cars, prev_results

    # Reset link for this run
    link = None

    # Initialize driver
    driver = setup_driver()
    try:
        driver.get("https://mobile.de")

        # Accept GDPR consent if button appears
        try:
            gdpr_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (By.ID, "gdpr-consent-layer-accept-all-button")
                )
            )
            gdpr_button.click()
            time.sleep(2)  # Allow time for the page to update
        except Exception as e:
            print("No GDPR consent popup found, continuing...")

        # # Click the search button
        consent_button = WebDriverWait(driver, 3000).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button.mde-consent-accept-btn")
            )
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
            search_button = driver.find_element(
                By.XPATH, "//button[@data-testid='qs-submit-button']"
            )
            search_button.click()
        except Exception as e:
            print("Search button not found, continuing...")
        time.sleep(3)

        # # Wait for search results to update after sorting and filtering
        results = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//article[@class='A3G6X vTKPY' and not(@data-testid)]")
            )  # Or a more specific selector for results
        )
        print(results)
        #
        print(f"Found {len(results)} results after sorting and filtering.")

        original_window = driver.current_window_handle
        # Extract and print car information (optional, can be re-enabled)
        all_windows_before_click = set(
            driver.window_handles
        )  # Use a set for easier difference
        for result in results[1:]:
            if result not in prev_results:
                prev_results.append(result)
                try:
                    driver.execute_script(
                        "arguments[0].scrollIntoView({behavior: 'auto', block: 'center', inline: 'center'});",
                        result,
                    )
                    time.sleep(3)
                    title = result.find_element(
                        By.XPATH, ".//span[contains(text(), 'Honda S2000')]"
                    )
                    print(title)
                    title.click()

                except Exception as e:
                    print("Could not extract details for one of the results:", e)
        for result in prev_results:
            time.sleep(2)
            #
            all_windows_after_click = set(driver.window_handles)
            new_window_handles = all_windows_after_click - all_windows_before_click
            new_window_handle = new_window_handles.pop()
            # Close the current tab
            driver.switch_to.window(new_window_handle)
            link = driver.current_url
            print(f"Found car at URL: {link}")
            driver.close()
            # driver.switch_to.window(original_window)
            # time.sleep(5)

        time.sleep(5000)
    except Exception as e:
        print("An error occurred:", e)


# finally:
#     driver.quit()
if __name__ == "__main__":
    run_search()
    # driver.quit()
