import time
from .base_test import BaseTest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from .cluster_operator import ClusterManager, IgnoreRule

class Compliance(BaseTest):
    def run(self):
        self.login()
        try:
            self.navigate_to_compliance()
        finally:
            self.perform_cleanup()
            print("Compliance test completed")

    def navigate_to_compliance(self):
        driver = self._driver
        interaction_manager = self._interaction_manager
        
        # Click on the compliance
        try:
            wait = WebDriverWait(driver, 10, 0.001)
            wait.until(EC.presence_of_element_located((By.ID, 'configuration-scanning-left-menu-item')))
            compliance = driver.find_element(By.ID, 'configuration-scanning-left-menu-item')
            driver.execute_script("arguments[0].click();", compliance)
        except:
            print("failed to click on compliance")
            driver.save_screenshot(f"./failed_to_click_on_compliance_{ClusterManager.get_current_timestamp()}.png")
        
        # Click on the cluster (the first one) 
        time.sleep(1)
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/armo-root/div/div/div/armo-config-scanning-page/div[2]/armo-cluster-scans-table/table/tbody/tr[1]/td[2]')))
            cluster = driver.find_element(By.XPATH, '/html/body/armo-root/div/div/div/armo-config-scanning-page/div[2]/armo-cluster-scans-table/table/tbody/tr[1]/td[2]')
            driver.execute_script("arguments[0].click();", cluster)
            print("First Cluster selected")
        except:
            print("failed to click on the cluster")
            driver.save_screenshot(f"./failed_to_click_on_the_cluster_{ClusterManager.get_current_timestamp()}.png")
        
        time.sleep(1)
        # click on ID filter
        try:
            id_button = "//button[.//span[contains(text(), 'Control ID')]]"
            id_element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, id_button)))
            id_element.click()
            print("ID filter button clicked")
        except:
            print("failed to click on ID filter button")
            driver.save_screenshot(f"./failed_to_click_on_ID_filter_button_{ClusterManager.get_current_timestamp()}.png")

        # set 262 for C-0262 control
        try:
            time.sleep(0.5)
            input_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.search-input")))
            input_element.clear()
            input_element.send_keys("262")
            print("262 for C-0262 control set")
        except: 
            print("failed to set 262 for C-00262 control")
            driver.save_screenshot(f"./failed_to_set_262_for_C-00262_control_{ClusterManager.get_current_timestamp()}.png")
        
        # choose the C-0262 control
        try:
            # Wait for the checkbox to be present
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".mat-checkbox"))
            )

            # Execute JavaScript to toggle the checkbox
            # Find the checkbox by its unique attribute, like a label or aria-label
            script = """
            let checkboxes = document.querySelectorAll('.mat-checkbox');
            for (let box of checkboxes) {
                let label = box.querySelector('.value.truncate');
                if (label && label.textContent.includes('C-0262')) {
                    box.click(); // Toggles the checkbox
                    break; // Assuming you only need to click the first matching checkbox
                }
            }
            """
            driver.execute_script(script)
            print("Checkbox of C-0262 clicked.")
        except Exception as e:
            print("Failed to click the checkbox.", str(e))
            driver.save_screenshot(f"./failed_to_click_c-0262_checkbox_{ClusterManager.get_current_timestamp()}.png")


        # click on the esc button
        ClusterManager.press_esc_key(driver)

        # # Click on the fix button
        try:
            time.sleep(0.5)                                        
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="configuration-scanning-controls-table"]/table/tbody/tr/td[10]/armo-fix-button/armo-button/button')))
            fix_button = driver.find_element(By.XPATH, '//*[@id="configuration-scanning-controls-table"]/table/tbody/tr/td[10]/armo-fix-button/armo-button/button')
            driver.execute_script("arguments[0].click();", fix_button)
            print("Fix button clicked")
        except:
            print("failed to click on fix button")
            driver.save_screenshot(f"./failed_to_click_on_fix_button_{ClusterManager.get_current_timestamp()}.png")
        
        # Wait until the side by side remediation page is visible
        WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) == 2)
        driver.switch_to.window(driver.window_handles[1])
        try:
            time.sleep(4)
            wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/armo-root/div/div/div/armo-side-by-side-remediation-page/div/armo-comparison-wrapper/div/div/div[1]/div/p')))
            parent_selector = "div.row-container.yaml-code-row"
            parent_element = driver.find_element(By.CSS_SELECTOR, parent_selector)

            # Find all armo-yaml-code elements within the parent element
            armo_yaml_code_elements = parent_element.find_elements(By.CSS_SELECTOR, "armo-yaml-code")
        except:
            print("side by side remediation page is not visible")
            driver.save_screenshot(f"./SBS_page_not_loaded_{ClusterManager.get_current_timestamp()}.png")

        # Check if there are exactly 2 child elements
        if len(armo_yaml_code_elements) == 2:
            # Count the number of rows in each armo-yaml-code element
            rows_count = [len(elm.find_elements(By.TAG_NAME, "tr")) for elm in armo_yaml_code_elements]

            # Compare the row counts of the two elements
            if rows_count[0] == rows_count[1]:
                print(f"Both armo-yaml-code elements have the same number of rows: {rows_count[0]} rows.")
            else:
                print(f"The armo-yaml-code elements have different numbers of rows: {rows_count[0]} and {rows_count[1]} rows.")

        else:
            print(f"The element contains {len(armo_yaml_code_elements)} armo-yaml-code child elements, not 2.")
        time.sleep(2)
        driver.switch_to.window(driver.window_handles[0])

        # Click on the resourse link (failed and accepted)
        try:
            resourse_link= wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="framework-control-table-failed-0"]/div/armo-router-link/a/armo-button/button')))
            resourse_link.click()                                          
        except: 
            print("failed to click on resourse link")
            driver.save_screenshot(f"./failed_to_click_on_the_resourse_link_{ClusterManager.get_current_timestamp()}.png")    
        
        # Wait until the table of the esourse is present  
        try:
            wait = WebDriverWait(driver, 60, 0.001)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "armo-button button.armo-button.primary.sm")))
            print("Table of the resourse is present")
        except:
            print("Table of the resourse is not present")
            driver.save_screenshot(f"./failed_to_find_the_resourse_table_{ClusterManager.get_current_timestamp()}.png")
        
        time.sleep(1)
        ignore_rule = IgnoreRule(driver)
        ignore_rule.click_ignore_button()
        time.sleep(2)
        resource_name = ignore_rule.get_ignore_rule_field(2)
        print(f"resource name: {resource_name}")
        time.sleep(1)
        ignore_rule.save_ignore_rule() 
        time.sleep(3)
        ignore_rule.igor_rule_icon_check()
        return resource_name
