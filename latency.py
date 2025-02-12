import os
import time
import datetime
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from dataclasses import dataclass
from selenium.webdriver.support.ui import WebDriverWait
from interaction_manager import InteractionManagerConfig
from interaction_manager import InteractionManager
import logging

ARMO_PLATFORM_URL = "https://cloud.armosec.io"

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
        result = self._interaction_manager.driver.save_screenshot(
            screenshot_name)
        if result is False:
            _logger.error("Failed to take screenshot")  # pragma: no cover
            raise RuntimeError("Failed to take screenshot")
        _logger.info(f"Screenshot saved to: {screenshot_name}")

    def _login(self) -> None:
        _logger.info("Logging in to Armo")
        driver = self._interaction_manager._driver
        driver.get(ARMO_PLATFORM_URL)   

        # Wait for initial page load
        time.sleep(5)

        shadow_host = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "frontegg-login-box-container-default")))

        # Get the shadow root
        shadow_root = self._interaction_manager.driver.execute_script("return arguments[0].shadowRoot", shadow_host)

        # Find the email input field inside the shadow DOM
        email_input = shadow_root.find_element(By.CSS_SELECTOR, "input[name='identifier']")
        email_input.send_keys(os.environ['email_latency'])
        email_input.send_keys(Keys.ENTER)
        time.sleep(2)
        driver.save_screenshot("email.png")
        #Wait for the password field to appear
        WebDriverWait(driver, 10).until(
            lambda d: shadow_root.find_element(By.CSS_SELECTOR, "input[name='password']")
        )

        #Find the password input field inside the shadow DOM
        password_input = shadow_root.find_element(By.CSS_SELECTOR, "input[name='password']")
        password_input.send_keys(os.environ['login_pass_latency'])
        password_input.send_keys(Keys.ENTER)
        print("Login successful!")

    def _navigate_to_compliance(self) -> None:
        _logger.info("Navigating to compliance")
        # Click on the compliance tab.
        self._interaction_manager.click('//*[@id="configuration-scanning-left-menu-item"]')
        # Click on the cluster (the first one).
        self._interaction_manager.click('/html/body/armo-root/div/div/div/armo-config-scanning-page/div[2]/armo-cluster-scans-table/table/tbody/tr[1]/td[2]')
        # Click on the failed resource button.
        self._interaction_manager.click('//*[@id="framework-control-table-failed-0"]/div/armo-router-link/a/armo-button/button', click_delay=1)
        # Click on the fix button in the rules list.
        self._interaction_manager.click("//button[contains(@class, 'armo-button') and contains(@class, 'primary') and contains(@class, 'sm') and span[text()='Fix']]", click_delay=1)
                                        
        # Switch to the last window.
        # self._interaction_manager.switch_to_window(-1)
        time.sleep(2)
        SBS_panel =self._interaction_manager.wait_until_exists('//*[@id="s-0-yaml-row-0"]', timeout=5)
        _logger.info(f"side bt side is displayed: {SBS_panel.is_displayed()}")
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
