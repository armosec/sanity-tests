import os
import time
import datetime
import logging
from dataclasses import dataclass
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, WebDriverException
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

class LatencyTest:
    def __init__(self) -> None:
        _config = InteractionManagerConfig.from_env()
        self._interaction_manager = InteractionManager(_config)

    def _take_screen_shot(self, description: str) -> None:
        """Take a screenshot for debugging."""
        _logger.info(f"Taking screenshot: {description}")
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        screenshot_name = f"{timestamp}_{description}.png"
        result = self._interaction_manager.driver.save_screenshot(screenshot_name)
        if not result:
            _logger.error("Failed to take screenshot")  
            raise RuntimeError("Failed to take screenshot")
        _logger.info(f"Screenshot saved to: {screenshot_name}")

    def wait_for_page_load(self, driver, timeout=20):
        """Waits for the page to be fully loaded."""
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

    def get_shadow_root(self, driver, max_retries=5):
        """Fetch the shadow root dynamically with retries to avoid stale references."""
        for attempt in range(max_retries):
            try:
                _logger.info(f"Attempt {attempt+1}: Waiting for page to load before getting shadow root")
                WebDriverWait(driver, 15).until(lambda d: d.execute_script("return document.readyState") == "complete")

                _logger.info(f"Attempt {attempt+1}: Finding shadow host element")
                shadow_host = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "frontegg-login-box-container-default"))
                )
                
                if shadow_host:
                    _logger.info(f"Attempt {attempt+1}: Executing script to retrieve shadow root")
                    shadow_root = driver.execute_script("return arguments[0].shadowRoot", shadow_host)

                    # Verify shadow root has content before returning
                    if shadow_root and shadow_root.find_elements(By.CSS_SELECTOR, "input[name='identifier']"):
                        _logger.info("Successfully retrieved shadow root!")
                        return shadow_root

            except (StaleElementReferenceException, TimeoutException, WebDriverException) as e:
                _logger.warning(f"Retrying shadow root fetch... Attempt {attempt + 1}/{max_retries}: {str(e)}")
                self._take_screen_shot(f"shadow_root_error_attempt_{attempt+1}")
                time.sleep(2)

        # **Final Check Before Failing**
        shadow_host_check = driver.find_elements(By.ID, "frontegg-login-box-container-default")
        if not shadow_host_check:
            _logger.error("Shadow host element does not exist on the page!")
        else:
            _logger.error("Shadow root could not be retrieved, but shadow host is present!")

        raise RuntimeError("Failed to get shadow root after multiple attempts")


    def _login(self) -> None:
        """Handles logging into the Armo platform using shadow DOM elements."""
        _logger.info("Logging in to Armo")
        driver = self._interaction_manager._driver
        driver.get(ARMO_PLATFORM_URL)   

        #  Ensure the page is fully loaded
        self.wait_for_page_load(driver)

        #  Step 1: Find and Input Email
        for attempt in range(3):
            try:
                shadow_root = self.get_shadow_root(driver)  # Always fetch fresh shadow root
                email_input = WebDriverWait(driver, 15).until(
                    lambda d: self.get_shadow_root(driver).find_element(By.CSS_SELECTOR, "input[name='identifier']")
                )
                email_input.send_keys(os.environ['email_latency'])
                email_input.send_keys(Keys.ENTER)
                break
            except (StaleElementReferenceException, TimeoutException, WebDriverException) as e:
                _logger.warning(f"Retrying email input... Attempt {attempt + 1}/3: {str(e)}")
                self._take_screen_shot("email_input_error")
                time.sleep(1)

        time.sleep(2)
        driver.save_screenshot("email.png")  # Debugging

        #  Step 2: Wait for Password Field
        WebDriverWait(driver, 10).until(
            lambda d: self.get_shadow_root(driver).find_element(By.CSS_SELECTOR, "input[name='password']")
        )

        #  Step 3: Find and Input Password
        for attempt in range(3):
            try:
                shadow_root = self.get_shadow_root(driver)  # Fetch fresh shadow root again
                password_input = shadow_root.find_element(By.CSS_SELECTOR, "input[name='password']")
                password_input.send_keys(os.environ['login_pass_latency'])
                password_input.send_keys(Keys.ENTER)
                break
            except (StaleElementReferenceException, TimeoutException, WebDriverException) as e:
                _logger.warning(f"Retrying password input... Attempt {attempt + 1}/3: {str(e)}")
                self._take_screen_shot("password_input_error")
                time.sleep(1)

        _logger.info("Login successful!")

    def _navigate_to_compliance(self) -> None:
        """Navigate to compliance section in Armo UI."""
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
        """Execute login and compliance navigation while measuring latency."""
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
