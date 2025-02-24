import os
import time
import datetime
import logging
from dataclasses import dataclass
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from interaction_manager import InteractionManagerConfig, InteractionManager

# Constants
ARMO_PLATFORM_URL = "https://cloud.armosec.io"

# Logging
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

@dataclass
class LatencyDetails:
    latency: float
    latency_without_login: float

    def to_file(self, file_path: str) -> None:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(file_path, "a") as f:
            f.write(f"{timestamp},{self.latency},{self.latency_without_login}\n")

    def __str__(self) -> str:
        return f"Latency: {self.latency}, Latency without login: {self.latency_without_login}"

    def __repr__(self) -> str:
        return self.__str__()

class LatencyTest:
    def __init__(self) -> None:
        _config = InteractionManagerConfig.from_env()
        self._interaction_manager = InteractionManager(_config)

    def _take_screen_shot(self, description: str) -> None:
        _logger.info(f"Taking screenshot: {description}")
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        screenshot_name = f"{timestamp}_{description}.png"
        result = self._interaction_manager.driver.save_screenshot(screenshot_name)
        if result is False:
            _logger.error("Failed to take screenshot")  
            raise RuntimeError("Failed to take screenshot")
        _logger.info(f"Screenshot saved to: {screenshot_name}")

    def wait_for_page_load(self, driver, timeout=20):
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

    def get_shadow_root(self, driver, max_retries=5):
        """Fetch the shadow root dynamically with retries to avoid stale references."""
        for attempt in range(max_retries):
            try:
                _logger.info(f"Attempt {attempt+1}: Getting shadow root")
                
                # Ensure the page is fully loaded
                self.wait_for_page_load(driver)
                
                # Explicitly wait for the shadow host element to appear
                shadow_host = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.ID, "frontegg-login-box-container-default"))
                )
                
                # Check if the element is still attached
                if not driver.execute_script("return document.contains(arguments[0]);", shadow_host):
                    _logger.warning(f"Attempt {attempt+1}: Shadow host is no longer attached to DOM. Retrying...")
                    time.sleep(2)
                    continue
                
                # Ensure shadow root exists before returning it
                shadow_root = driver.execute_script("return arguments[0].shadowRoot", shadow_host)
                
                if shadow_root:
                    _logger.info("Successfully retrieved shadow root!")
                    return shadow_root
                
                _logger.warning("Shadow root is not yet available, retrying...")
                
            except (StaleElementReferenceException, TimeoutException) as e:
                _logger.warning(f"Retrying shadow root fetch... Attempt {attempt + 1}/{max_retries}: {str(e)}")
                time.sleep(2)
            
        driver.save_screenshot("shadow_root_error.png")
        raise RuntimeError("Failed to get shadow root after multiple attempts")


    def _login(self) -> None:
        """Handles logging into the Armo platform using shadow DOM elements."""
        _logger.info("Logging in to Armo")
        driver = self._interaction_manager.driver
        
        driver.get(ARMO_PLATFORM_URL)
        self.wait_for_page_load(driver)

        # Clear cookies and storage to avoid stale sessions
        try:
            driver.delete_all_cookies()
            driver.execute_script("window.localStorage.clear();")
            driver.execute_script("window.sessionStorage.clear();")
        except Exception as e:
            _logger.warning(f"Failed to clear storage: {e}")

        time.sleep(3)  # Ensure JavaScript elements are fully initialized

        try:
            shadow_root = self.get_shadow_root(driver)

            email_input = WebDriverWait(driver, 20).until(
                lambda d: shadow_root.find_element(By.CSS_SELECTOR, "input[name='identifier']")
            )
            email_input.clear()
            email_input.send_keys(os.environ['email_latency'])
            email_input.send_keys(Keys.ENTER)

            time.sleep(2)
            shadow_root = self.get_shadow_root(driver)

            password_input = WebDriverWait(driver, 20).until(
                lambda d: shadow_root.find_element(By.CSS_SELECTOR, "input[name='password']")
            )
            password_input.clear()
            password_input.send_keys(os.environ['login_pass_latency'])
            password_input.send_keys(Keys.ENTER)

            WebDriverWait(driver, 30).until(
                lambda d: "login" not in d.current_url.lower()
            )

            _logger.info("Login successful!")

        except TimeoutException:
            driver.save_screenshot("login_timeout_error.png")
            raise Exception("Login failed due to timeout.")

        except Exception as e:
            driver.save_screenshot("login_error.png")
            
            # If login fails, attempt a page refresh and retry login once
            _logger.warning(f"Login attempt failed: {str(e)}. Retrying after page refresh.")
            driver.refresh()
            time.sleep(5)
            
            try:
                self._login()  # Retry login once
            except Exception as retry_error:
                raise Exception(f"Login failed after retry: {str(retry_error)}")


    def _navigate_to_compliance(self) -> None:
        _logger.info("Navigating to compliance")
        self._interaction_manager.click('//*[@id="configuration-scanning-left-menu-item"]')
        self._interaction_manager.click('/html/body/armo-root/div/div/div/armo-config-scanning-page/div[2]/armo-cluster-scans-table/table/tbody/tr[1]/td[2]')
        self._interaction_manager.click('//*[@id="framework-control-table-failed-0"]/div/armo-router-link/a/armo-button/button', click_delay=1)
        self._interaction_manager.click("//button[contains(@class, 'armo-button') and contains(@class, 'primary') and contains(@class, 'sm') and span[text()='Fix']]", click_delay=1)
                                            
        time.sleep(2)
        SBS_panel = self._interaction_manager.wait_until_exists('//*[@id="s-0-yaml-row-0"]', timeout=5)
        _logger.info(f"Side-by-side panel displayed: {SBS_panel.is_displayed()}")
        _logger.info("Navigated to compliance completed")

    def run(self) -> None:
        start_time = time.time()
        self._login()
        login_time = time.time()
        self._navigate_to_compliance()
        end_time = time.time()
        latency_without_login = "{:.2f}".format(end_time - login_time)
        latency = "{:.2f}".format(end_time - start_time)
        latency_details = LatencyDetails(latency, latency_without_login)
        latency_details.to_file("./logs/latency_logs.csv")
        _logger.info(f"Latency details: {latency_details}")
        self._interaction_manager.quit()

if __name__ == "__main__":
    LatencyTest().run()
