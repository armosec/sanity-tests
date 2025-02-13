import os
import time
import datetime
import logging
from dataclasses import dataclass
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
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
        """Take a screenshot for debugging."""
        _logger.info(f"Taking screenshot: {description}")
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        screenshot_name = f"{timestamp}_{description}.png"
        result = self._interaction_manager.driver.save_screenshot(screenshot_name)
        if result is False:
            _logger.error("Failed to take screenshot")  
            raise RuntimeError("Failed to take screenshot")
        _logger.info(f"Screenshot saved to: {screenshot_name}")

    def get_shadow_root(self, driver):
        """Fetch the shadow root dynamically to prevent detachment issues."""
        shadow_host = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "frontegg-login-box-container-default"))
        )
        return driver.execute_script("return arguments[0].shadowRoot", shadow_host)

    def _login(self) -> None:
        """Handles logging into the Armo platform using shadow DOM elements."""
        _logger.info("Logging in to Armo")
        driver = self._interaction_manager._driver
        driver.get(ARMO_PLATFORM_URL)   

        # Wait for page load
        time.sleep(3)

        # Retrieve shadow root dynamically
        shadow_root = self.get_shadow_root(driver)

        #Step 1: Find and Input Email
        email_input = WebDriverWait(driver, 15).until(
            lambda d: self.get_shadow_root(driver).find_element(By.CSS_SELECTOR, "input[name='identifier']")
        )
        email_input.send_keys(os.environ['email_latency'])
        email_input.send_keys(Keys.ENTER)
        time.sleep(2)
        # driver.save_screenshot("email.png")  # Debugging

        # Step 2: Wait for Password Field
        WebDriverWait(driver, 10).until(
            lambda d: self.get_shadow_root(driver).find_element(By.CSS_SELECTOR, "input[name='password']")
        )

        # Step 3: Find and Input Password
        password_input = self.get_shadow_root(driver).find_element(By.CSS_SELECTOR, "input[name='password']")
        password_input.send_keys(os.environ['login_pass_latency'])
        password_input.send_keys(Keys.ENTER)
        
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
