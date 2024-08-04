# tests/compliance.py
import time
import logging
from .base_test import BaseTest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from .cluster_operator import ClusterManager, IgnoreRule, ConnectCluster , RiskAcceptancePage

logger = logging.getLogger(__name__)

class Compliance(BaseTest):
    # def __init__(self, config):
    #     super().__init__(config)
    #     self.connect_cluster = ConnectCluster(self._driver, self._wait)
    #     self.cluster_manager = ClusterManager(self._driver, self._wait)
    
    def run(self):
        self.connect_cluster = ConnectCluster(self._driver, self._wait)
        self.cluster_manager = ClusterManager(self._driver, self._wait)
        login_url = self.get_login_url()
        self.login(login_url)
        try:
            self.connect_cluster.click_get_started()
            self.connect_cluster.connect_cluster_helm()
            self.connect_cluster.verify_installation()
            self.connect_cluster.view_cluster_button()
            self.connect_cluster.view_connected_cluster()
            self.navigate_to_compliance()
            self.risk_acceptance_page()
        finally:
            self.perform_cleanup()
            print("Compliance test completed")

    def navigate_to_compliance(self):
        driver = self._driver
        interaction_manager = self._interaction_manager
        
        try:
            interaction_manager.click('configuration-scanning-left-menu-item', By.ID)
            logger.info("Compliance clicked")
        except:
            logger.error("failed to click on compliance")
            driver.save_screenshot(f"./failed_to_click_on_compliance_{ClusterManager.get_current_timestamp()}.png")
        
        # Click on the cluster (the first one) 
        time.sleep(1)
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/armo-root/div/div/div/armo-config-scanning-page/div[2]/armo-cluster-scans-table/table/tbody/tr[1]/td[2]')))
            cluster = driver.find_element(By.XPATH, '/html/body/armo-root/div/div/div/armo-config-scanning-page/div[2]/armo-cluster-scans-table/table/tbody/tr[1]/td[2]')
            driver.execute_script("arguments[0].click();", cluster)
            logger.info("First Cluster selected")
        except:
            logger.error("failed to click on the cluster")
            driver.save_screenshot(f"./failed_to_click_on_the_cluster_{ClusterManager.get_current_timestamp()}.png")
        
        time.sleep(1)
        # click on ID filter
        try:
            id_button = "//button[.//span[contains(text(), 'Control ID')]]"
            id_element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, id_button)))
            id_element.click()
            logger.info("ID filter button clicked")
        except:
            logger.error("failed to click on ID filter button")
            driver.save_screenshot(f"./failed_to_click_on_ID_filter_button_{ClusterManager.get_current_timestamp()}.png")

        try:
            time.sleep(0.5)
            input_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.search-input")))
            input_element.clear()
            input_element.send_keys("271")
            logger.info("271 for C-0271 control set")
        except: 
            print("failed to set 271 for C-00271 control")
            driver.save_screenshot(f"./failed_to_set_271_for_C-00271_control_{ClusterManager.get_current_timestamp()}.png")
        
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".mat-checkbox"))
            )
            script = """
            let checkboxes = document.querySelectorAll('.mat-checkbox');
            for (let box of checkboxes) {
                let label = box.querySelector('.value.truncate');
                if (label && label.textContent.includes('C-0271')) {
                    box.click(); // Toggles the checkbox
                    break; // Assuming you only need to click the first matching checkbox
                }
            }
            """
            driver.execute_script(script)
            logger.info("Checkbox of C-0271 clicked.")
        except Exception as e:
            logger.error("Failed to click the checkbox.", str(e))
            driver.save_screenshot(f"./failed_to_click_c-0271_checkbox_{ClusterManager.get_current_timestamp()}.png")

        ClusterManager.press_esc_key(driver)

        try:
            time.sleep(0.5)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="configuration-scanning-controls-table"]/table/tbody/tr/td[10]/armo-fix-button/armo-button/button')))
            fix_button = driver.find_element(By.XPATH, '//*[@id="configuration-scanning-controls-table"]/table/tbody/tr/td[10]/armo-fix-button/armo-button/button')
            driver.execute_script("arguments[0].click();", fix_button)
            logger.info("Fix button clicked")
        except:
            logger.error("failed to click on fix button")
            driver.save_screenshot(f"./failed_to_click_on_fix_button_{ClusterManager.get_current_timestamp()}.png")
        
        # Wait until the side by side remediation page is visible
        WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) == 2)
        driver.switch_to.window(driver.window_handles[1])
        try:
            time.sleep(4)
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '/html/body/armo-root/div/div/div/armo-side-by-side-remediation-page/div/armo-comparison-wrapper/div/div/div[1]/div/p')))
            parent_selector = "div.row-container.yaml-code-row"
            parent_element = driver.find_element(By.CSS_SELECTOR, parent_selector)

            # Find all armo-yaml-code elements within the parent element
            armo_yaml_code_elements = parent_element.find_elements(By.CSS_SELECTOR, "armo-yaml-code")
        except:
            logger.error("side by side remediation page is not visible")
            driver.save_screenshot(f"./SBS_page_not_loaded_{ClusterManager.get_current_timestamp()}.png")

        # Check if there are exactly 2 child elements
        if len(armo_yaml_code_elements) == 2:
            # Count the number of rows in each armo-yaml-code element
            rows_count = [len(elm.find_elements(By.TAG_NAME, "tr")) for elm in armo_yaml_code_elements]

            # Compare the row counts of the two elements
            if rows_count[0] == rows_count[1]:
                logger.info(f"Both armo-yaml-code elements have the same number of rows: {rows_count[0]} rows.")
            else:
                logger.error(f"The armo-yaml-code elements have different numbers of rows: {rows_count[0]} and {rows_count[1]} rows.")
        else:
            logger.error(f"The element contains {len(armo_yaml_code_elements)} armo-yaml-code child elements, not 2.")
        
        time.sleep(2)
        driver.switch_to.window(driver.window_handles[0])

        # Click on the resourse link (failed and accepted)
        try:
            resourse_link= WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="framework-control-table-failed-0"]/div/armo-router-link/a/armo-button/button')))
            resourse_link.click()                                          
        except: 
            logger.error("failed to click on resourse link")
            driver.save_screenshot(f"./failed_to_click_on_the_resourse_link_{ClusterManager.get_current_timestamp()}.png")    
        
        # Wait until the table of the esourse is present  
        try:
            WebDriverWait(driver, 60, 0.001).until(EC.presence_of_element_located((By.CSS_SELECTOR, "armo-button button.armo-button.primary.sm")))
            logger.info("Table of the resourse is present")
        except:
            logger.error("Table of the resourse is not present")
            driver.save_screenshot(f"./failed_to_find_the_resourse_table_{ClusterManager.get_current_timestamp()}.png")
        
        time.sleep(1)
        ignore_rule = IgnoreRule(driver)
        ignore_rule.click_ignore_button()
        time.sleep(2)
        resource_name = ignore_rule.get_ignore_rule_field(2)
        logger.info(f"resource name: {resource_name}")
        time.sleep(1)
        ignore_rule.save_ignore_rule() 
        time.sleep(3)
        ignore_rule.igor_rule_icon_check()
        return resource_name
    
    def risk_acceptance_page(self):
        risk_acceptance = RiskAcceptancePage(self._driver)
        time.sleep(3)
        risk_acceptance.navigate_to_page()
        print("Navigated to Risk Acceptance page")
        risk_acceptance.switch_tab("Compliance")
        time.sleep(1)
        risk_acceptance.click_severity_element("td.mat-cell.cdk-column-posturePolicies-0-severityScore")
        time.sleep(1)
        risk_acceptance.click_edit_button("//armo-button[@buttontype='primary']//button[text()='Edit']")
        time.sleep(2.5)
        risk_acceptance.delete_ignore_rule()
        time.sleep(3)
