# tests/attach_path.py
import time
import logging
from .base_test import BaseTest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from .cluster_operator import ClusterManager

logger = logging.getLogger(__name__)

class AttachPath(BaseTest):
    def run(self):
        cluster_manager = ClusterManager(self._driver, self._wait)
        cluster_manager.create_attack_path()  
        login_url = self.get_login_url()
        self.login(login_url)
        try:
            self.navigate_to_attach_path()
        finally:
            logger.info("Attach path test completed")

    def navigate_to_attach_path(self):
        driver = self._driver
        wait = self._wait
        try:
            attack_path_element = wait.until(EC.element_to_be_clickable((By.ID, "attack-path-left-menu-item")))
            attack_path_element.click()
            logger.info("Attach-path clicked.")
        except:
            logger.error("Attach path not found.")
            driver.save_screenshot(f"./failed_to_click_attach_path_{ClusterManager.get_current_timestamp()}.png")

        # Check if the Attack path is displayed
        try:
            data_test_id = "attack-chains-list"
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, f"[data-test-id='{data_test_id}']")))
            logger.info("Attack path is displayed.")

            # Obtain descriptions
            descriptions = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-test-id='description']")))

            if len(descriptions) < 2:
                logger.error(f"Expected 2 elements with 'data-test-id=description', found {len(descriptions)}")
                driver.save_screenshot(f"./failed_to_find_descriptions_{ClusterManager.get_current_timestamp()}.png")
                
            else:
                logger.info(f"Found {len(descriptions)} elements with data-test-id=description")

                # Verify and click first description
                self.verify_and_click_description(0, wait, driver)

                try:
                    # link = driver.find_element(By.XPATH, "/html/body/armo-root/div/div/div/armo-attack-chain-details-page/div[1]/armo-attack-chain-details-breadcrumb-container/armo-breadcrumbs/ul/li[1]/a/armo-button/button")
                    link = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'armo-button') and contains(@class, 'tertiary') and contains(@class, 'lg') and text()=' Attack Path ']")))
                    link.click()
                    logger.info("Clicked on 'Attack Path' link.")
                except NoSuchElementException:
                    logger.error("Link not found.")
                time.sleep(1)
                # Verify and click second description
                self.verify_and_click_description(1, wait, driver)

        except NoSuchElementException:
            logger.error("Attack path is NOT displayed.")
            driver.save_screenshot(f"./failed_to_find_the_attack_path_{ClusterManager.get_current_timestamp()}.png")

    def verify_and_click_description(self, index, wait, driver):
        try:
            descriptions = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-test-id='description']")))
            description_element = descriptions[index]
            description_element.click()
            logger.info(f"Clicked on description {index + 1}.")
        except:
            logger.error(f"Failed to click on description {index + 1}.")
            driver.save_screenshot(f"./failed_to_click_description_{index + 1}_{ClusterManager.get_current_timestamp()}.png")
