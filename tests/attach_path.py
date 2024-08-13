# tests/attach_path.py
import time
import logging
import json
from .base_test import BaseTest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from .cluster_operator import ClusterManager
from .interaction_manager import InteractionManager

logger = logging.getLogger(__name__)

class AttachPath(BaseTest):
    def run(self):
        cluster_manager = ClusterManager(self._driver, self._wait)
        cluster_manager.create_attack_path()
        login_url = self.get_login_url()
        self.login(login_url)
        try:
            print("Running Attach Path test")
            self.navigate_to_attach_path()
        finally:
            logger.info("Attach path test completed")

    def navigate_to_attach_path(self):
        driver = self._driver
        wait = self._wait
        interaction_manager = InteractionManager(driver)
        try:
            interaction_manager.click("attack-path-left-menu-item", by=By.ID)
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
                driver.save_screenshot(f"./failed_to_find_AC_{ClusterManager.get_current_timestamp()}.png")
            else:
                logger.info(f"Found {len(descriptions)} elements with data-test-id=description")

                # Verify and click first description(attack path)
                self.click_on_attach_path(0, wait, driver, interaction_manager)

                try:
                    interaction_manager.click("//button[contains(@class, 'armo-button') and contains(@class, 'tertiary') and contains(@class, 'lg') and text()=' Attack Path ']", by=By.XPATH)
                    logger.info("Clicked on 'Attack Path' link.")
                except NoSuchElementException:
                    logger.error("Link not found.")
                time.sleep(1)
                # Verify and click second description(attack path)
                self.click_on_attach_path(1, wait, driver, interaction_manager)
                    



        except NoSuchElementException:
            logger.error("Attack path is NOT displayed.")
            driver.save_screenshot(f"./failed_to_find_the_attack_path_{ClusterManager.get_current_timestamp()}.png")

    def click_on_attach_path(self, index, wait, driver, interaction_manager):
        try:
            descriptions = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-test-id='description']")))
            description_element = descriptions[index]
            description_element.click()
            logger.info(f"Clicked on description {index + 1}.")
            if self.check_table_exists(driver):
                attack_path_element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "armo-vulnerabilities-shared-table")))
                print(f"Found the {attack_path_element}")
                self.validate_graph(interaction_manager, attack_path_element)
                self.extract_graph_data(driver)
                 # Validate the SVG graph
                if self.validate_graph(interaction_manager):
                    logger.info("SVG graph validation passed.")
                else:
                    logger.error("graph validation failed.")
                    driver.save_screenshot(f"./failed_svg_graph_validation_{ClusterManager.get_current_timestamp()}.png")   
            else:
                attack_path_element = wait.until(EC.element_to_be_clickable((By.ID, "attack_path_element")))
                
                

        except:
            logger.error(f"Failed to click on description {index + 1}.")
            driver.save_screenshot(f"./failed_to_click_description_{index + 1}_{ClusterManager.get_current_timestamp()}.png")
            
    def check_table_exists(driver, timeout=10):
        try:
            # Wait until the element is present on the page
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "armo-vulnerabilities-shared-table"))
            )
            print("Found the armo-vulnerabilities-shared-table element")
            return True
        except:
            print("armo-vulnerabilities-shared-table element not found")
            return False 

    def validate_graph(self, interaction_manager, attack_path_element):
        try:
            # Extract current graph data
            current_graph_data = self.extract_graph_data(interaction_manager)

            # Load baseline graph data
            if attack_path_element == "armo-vulnerabilities-shared-table":
                with open('./tests/vulnerabilities.json', 'r') as file:
                    baseline_graph_data = json.load(file)
            else:
                with open('./tests/vulnerabilities.json', 'r') as file:
                    baseline_graph_data = json.load(file)

            # Compare current graph data with baseline
            return current_graph_data == baseline_graph_data
        except Exception as e:
            logger.error(f"Graph validation error: {str(e)}")
            return False

    def extract_graph_data(self, driver):
        # Wait until the SVG element is present
        try:
            svg_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "svg.grab"))
            )
        except TimeoutException:
            self.logger.error("SVG element not found on the page.")
            driver.save_screenshot(f"./svg_element_not_found_{ClusterManager.get_current_timestamp()}.png")
            return None

        # Extract paths and other relevant data from the SVG
        paths = svg_element.find_elements(By.CSS_SELECTOR, "path")
        graph_data = []
        for path in paths:
            graph_data.append({
                "id": path.get_attribute("id"),
                "d": path.get_attribute("d"),
                "stroke-width": path.get_attribute("stroke-width"),
                "marker-end": path.get_attribute("marker-end")
            })


    # def click_on_attach_path(self, index, wait, driver, interaction_manager):
    #     try:
    #         descriptions = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-test-id='description']")))
    #         description_element = descriptions[index]
    #         interaction_manager.click(description_element, by=By.CSS_SELECTOR)
    #         logger.info(f"Clicked on description {index + 1}.")
    #         if self.check_table_exists(driver):
    #             interaction_manager.click("armo-vulnerabilities-shared-table", by=By.CSS_SELECTOR)
    #     except:
    #         logger.error(f"Failed to click on description {index + 1}.")
    #         driver.save_screenshot(f"./failed_to_click_description_{index + 1}_{ClusterManager.get_current_timestamp()}.png")