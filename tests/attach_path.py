import time
import logging
import json
from .base_test import BaseTest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from .cluster_operator import ClusterManager, IgnoreRule, RiskAcceptancePage
from .interaction_manager import InteractionManager

logger = logging.getLogger(__name__)

class AttachPath(BaseTest):
    def run(self):
        cluster_manager = ClusterManager(self._driver, self._wait)
        cluster_manager.create_attack_path()
        login_url = self.get_login_url()
        self.login(login_url)
        try:
            logger.info("Running Attach Path test")
            self.navigate_to_attach_path()
            self.risk_acceptance_page()
        finally:
            logger.info("Attach path test completed")

    def navigate_to_attach_path(self):
        driver = self._driver
        wait = self._wait
        interaction_manager = InteractionManager(driver)
        try:
            interaction_manager.click("attack-path-left-menu-item", by=By.ID)
            logger.info("Attach-path clicked.")
        except Exception as e:
            logger.error(f"Attach path not found: {str(e)}")
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

                # Verify and click first description (attack path)
                self.click_on_attach_path(0, wait, driver, interaction_manager)

                try:
                    interaction_manager.click("//button[contains(@class, 'armo-button') and contains(@class, 'tertiary') and contains(@class, 'lg') and text()=' Attack Path ']", by=By.XPATH)
                    logger.info("Clicked on 'Attack Path' link.")
                except NoSuchElementException:
                    logger.error("Link not found.")
                time.sleep(1)
                
                # Verify and click second description (attack path)
                self.click_on_attach_path(1, wait, driver, interaction_manager)

        except NoSuchElementException:
            logger.error("Attack path is NOT displayed.")
            driver.save_screenshot(f"./failed_to_find_the_attack_path_{ClusterManager.get_current_timestamp()}.png")

    def click_on_attach_path(self, index, wait, driver, interaction_manager):
        cluster_manager = ClusterManager(driver, wait)
        try:
            descriptions = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-test-id='description']")))
            description_element = descriptions[index]
            description_element.click()
            logger.info(f"Clicked on description {index + 1}.")

            # Capture the returned table_id
            table_id = self.validate_attach_path_graph(driver, interaction_manager)
            if table_id == "attack-chain-vulnerabilities-table":
                self.create_ignore_rule(driver) 
                self._interaction_manager.click("node-Initial Access", by=By.ID)
                logger.info("Clicked on 'Initial Access' node.")
                control_row = wait.until(EC.presence_of_element_located((By.ID, "row-C-0256")))
                logger.info("Found control C-0256.")
                fix_button = driver.find_element(By.ID, "fix-button")
                try:
                    self._interaction_manager.click("fix-button", by=By.ID, index=2)
                    logger.info("Clicked on 'Fix' button.")
                except Exception as e:
                    logger.error(f"Failed to click on 'Fix' button: {str(e)}")
                    self._driver.save_screenshot(f"./failed_to_click_fix_button_{ClusterManager.get_current_timestamp()}.png")
                
                if self.compare_yaml_code_elements(self._driver, "div.row-container.yaml-code-row"):
                    logger.info("SBS yamls - The number of rows is equal .")
                else:
                    logger.error("SBS yamls - The number of rows is NOT equal.")
                cluster_manager.press_esc_key(driver)
            else:
                self._interaction_manager.click("fix-button", by=By.ID, index=2)
                if self.compare_yaml_code_elements(self._driver, "div.row-container.yaml-code-row"):
                    logger.info("SBS yamls - The number of rows is equal .")
                else:
                    logger.error("SBS yamls - The number of rows is NOT equal.")
                cluster_manager.press_esc_key(driver)
                
                
            

            
            
            
        except Exception as e:
            logger.error(f"Failed to click on description {index + 1}: {str(e)}")
            self._driver.save_screenshot(f"./failed_to_click_description_{index + 1}_{ClusterManager.get_current_timestamp()}.png")

        
    def validate_attach_path_graph(self, driver, interaction_manager):
        table_id = self.check_attach_path_kind(driver)
        if table_id:
            logger.info(f"Found the {table_id}")

            # Validate the graph based on the identified table type
            if self.validate_graph(interaction_manager, table_id):
                logger.info("Attach Path graph validation passed.")
                return table_id  # Return the table_id
            else:
                logger.error("Graph validation failed.")
                self._driver.save_screenshot(f"./failed_graph_validation_{ClusterManager.get_current_timestamp()}.png")
                return None
        else:
            logger.error("Attach path table not found.")
            self._driver.save_screenshot(f"./failed_to_find_attach_path_table_{ClusterManager.get_current_timestamp()}.png")
            return None  # Return None if no table is found


    def check_attach_path_kind(self, driver, timeout=5):
        try:
            # Check for 'attack-chain-controls-table'
            controls_table_present = self._wait.until(EC.presence_of_element_located((By.ID, "attack-chain-controls-table")))
            logger.info("Found 'attack-chain-controls-table'")
            return "attack-chain-controls-table"
        except TimeoutException:
            logger.info("'attack-chain-controls-table' not found, checking 'attack-chain-vulnerabilities-table'")

        try:
            # Check for 'attack-chain-vulnerabilities-table'
            vulnerabilities_table_present = self._wait.until(EC.presence_of_element_located((By.ID, "attack-chain-vulnerabilities-table")))
            logger.info("Found 'attack-chain-vulnerabilities-table'")
            return "attack-chain-vulnerabilities-table"
        except TimeoutException:
            logger.error("Neither 'attack-chain-controls-table' nor 'attack-chain-vulnerabilities-table' found")
            self._driver.save_screenshot(f"./failed_to_find_attack_chain_table_{ClusterManager.get_current_timestamp()}.png")
            return None

    def validate_graph(self, interaction_manager, table_id):
        try:
            # Extract current graph data
            current_graph_data = self.extract_graph_data(interaction_manager.driver)

            # Load baseline graph data
            if table_id == "attack-chain-vulnerabilities-table":
                with open('./tests/vulnerabilities.json', 'r') as file:
                    baseline_graph_data = json.load(file)
            else:
                with open('./tests/controls.json', 'r') as file:
                    baseline_graph_data = json.load(file)

            # Compare current graph data with baseline
            return current_graph_data == baseline_graph_data
        except Exception as e:
            logger.error(f"Graph validation error: {str(e)}")
            return False

    def extract_graph_data(self, driver):
        try:
            svg_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "svg.grab"))
            )
        except TimeoutException:
            logger.error("SVG element not found on the page.")
            driver.save_screenshot(f"./svg_element_not_found_{ClusterManager.get_current_timestamp()}.png")
            return None

        paths = svg_element.find_elements(By.CSS_SELECTOR, "path")
        graph_data = []
        for path in paths:
            graph_data.append({
                "id": path.get_attribute("id"),
                "d": path.get_attribute("d"),
                "stroke-width": path.get_attribute("stroke-width"),
                "marker-end": path.get_attribute("marker-end")
            })
        return graph_data
            
    def create_ignore_rule(self, driver):
        ignore_rule = IgnoreRule(driver)
        ignore_rule.click_ignore_button()
        logger.info("Clicked on the 'Accept Risk' button")
        time.sleep(1)
        container_name = ignore_rule.get_ignore_rule_field(3)
        logger.info(f"Container name: {container_name}")
        time.sleep(1)
        ignore_rule.save_ignore_rule() 
        time.sleep(3)
        ignore_rule.igor_rule_icon_check()
        return container_name
    
    def risk_acceptance_page(self):
        risk_acceptance = RiskAcceptancePage(self._driver)
        time.sleep(3)
        risk_acceptance.navigate_to_page()
        logger.info("Navigated to risk acceptance page")
        time.sleep(1)
        risk_acceptance.switch_tab("Vulnerabilities")
        risk_acceptance.click_severity_element("td.mat-cell.mat-column-vulnerabilities-0-severityScore")
        time.sleep(1)
        risk_acceptance.click_edit_button("//armo-button[@buttontype='primary']//button[text()='Edit']")
        time.sleep(2.5)
        risk_acceptance.delete_ignore_rule()
        time.sleep(3)
            
def compare_yaml_code_elements(driver, parent_selector: str, timeout: int = 10) -> bool:
    try:
        # Wait until the parent element is present
        parent_element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, parent_selector))
        )

        # Wait until all armo-yaml-code elements within the parent element are present
        armo_yaml_code_elements = WebDriverWait(parent_element, timeout).until(
            lambda element: element.find_elements(By.CSS_SELECTOR, "armo-yaml-code")
        )
    except (TimeoutException, NoSuchElementException):
        logger.error("Side by side remediation page is not visible")
        driver.save_screenshot(f"./SBS_page_not_loaded_{ClusterManager.get_current_timestamp()}.png")
        return False

    # Check if there are exactly 2 child elements
    if len(armo_yaml_code_elements) == 2:
        # Count the number of rows in each armo-yaml-code element
        rows_count = [len(elm.find_elements(By.TAG_NAME, "tr")) for elm in armo_yaml_code_elements]

        # Compare the row counts of the two elements
        if rows_count[0] == rows_count[1]:
            logger.info(f"Both armo-yaml-code elements have the same number of rows: {rows_count[0]} rows.")
            return True
        else:
            logger.error(f"The armo-yaml-code elements have different numbers of rows: {rows_count[0]} and {rows_count[1]} rows.")
            return False
    else:
        logger.error(f"The element contains {len(armo_yaml_code_elements)} armo-yaml-code child elements, not 2.")
        return False