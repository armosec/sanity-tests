import time
import logging
from .base_test import BaseTest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from .cluster_operator import ClusterManager, IgnoreRule, ConnectCluster, RiskAcceptancePage

logger = logging.getLogger(__name__)

class VulneCvePage(BaseTest):    
    def run(self):
        logger.info("Starting CVEs tab test")
        self.vulne_cve_test()

    def vulne_cve_test(self):
        driver = self._driver
        interaction_manager = self._interaction_manager
        cluster_manager = ClusterManager(self._driver, self._wait)
        try:
            interaction_manager.click('image-scanning-left-menu-item', By.ID)
            logger.info("Vulnerabilities clicked")
        except:
            logger.error("Failed to click on vulnerabilities")
            driver.save_screenshot(f"./failed_to_click_on_vulnerabilities_{ClusterManager.get_current_timestamp()}.png")
        
        time.sleep(1)    
        cluster_manager.click_filter_button("Namespace") 
        time.sleep(5)
        cluster_manager.click_checkbox_by_name("attack-suite")  #default
        time.sleep(1)
        ClusterManager.click_close_filter(driver)
        time.sleep(1)
        cluster_manager.click_filter_button("Workload")
        time.sleep(3)
        cluster_manager.click_checkbox_by_name("ping-app")   #alpine-deployment
        time.sleep(1)
        ClusterManager.click_close_filter(driver,index=1)
        time.sleep(1)   
        cluster_manager.click_filter_button("In Use")
        time.sleep(1)

        yes_inUse_xpath = "//li[contains(@class, 'd-flex align-items-center')]//span[text()='Yes']"
        yes_element = interaction_manager.wait_until_exists(yes_inUse_xpath, By.XPATH)
        driver.execute_script("arguments[0].click();", yes_element)
        logger.info("Successfully clicked 'Yes' in the 'In Use' filter.")

        ClusterManager.press_space_key(driver)  
        time.sleep(1)
        cluster_manager.click_filter_button("Severity")
        time.sleep(1)
        cluster_manager.click_checkbox_by_name("Medium") 
        time.sleep(1)
        ClusterManager.press_space_key(driver)     
        time.sleep(2)
        
        ignore_rule = IgnoreRule(driver)
        ignore_rule.click_ignore_button()
        logger.info("Clicked on the 'Accept Risk' button")
        time.sleep(1)
        ignore_rule.save_ignore_rule()
        
        time.sleep(2)
        # Click on the first row
        try:
            cve_cells = self._driver.find_elements(By.XPATH, "//span[contains(@class, 'medium-severity-color') and normalize-space(text())='Medium']")

            # Check if there are any elements found and click the first one
            if cve_cells:
                # cve_cells[2].click()
                interaction_manager.click("//span[contains(@class, 'medium-severity-color') and normalize-space(text())='Medium']", By.XPATH,index=2)
                logger.info("Clicked on the first matching CVE cell.")
            else:
                logger.error("No matching CVE cells found.")
                driver.save_screenshot(f"./no_matching_cve_cells_{ClusterManager.get_current_timestamp()}.png")
        except TimeoutException:
            logger.error("Failed to click on the first row")
            
        try:
            # Wait for a unique and stable element in the sidebar that appears after the click.
            sidebar_title_xpath = "//span[normalize-space(text())='Medium']"
            WebDriverWait(self._driver, 15).until(
                EC.visibility_of_element_located((By.XPATH, sidebar_title_xpath))
            )
            logger.info("CVE details table has appeared and is stable.")
        except TimeoutException:
            logger.error("CVE details table did not appear after clicking the CVE cell.")
            self._driver.save_screenshot(f"./cve_details_table_failed_to_load_{ClusterManager.get_current_timestamp()}.png")
            raise

        cve_severity = interaction_manager.get_text("//span[contains(@class, 'medium-severity-color') and normalize-space(text())='Medium']")
        logger.info(f"Severity: {cve_severity}")
     
        button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//armo-button[contains(@class, 'link-button') and .//button[contains(@class, 'armo-button') and contains(@class, 'tertiary') and contains(@class, 'sm')]]")))
        button.click()
        time.sleep(1)

        cluster_manager.click_tab_on_sidebar(tab_name="Runtime Analysis")
        time.sleep(1)
        
        # click on the bottom ">" in the saide panel
        cluster_manager.click_overlay_button()
        time.sleep(1)
        workload_name = interaction_manager.get_text("//span[text()='Workload']/ancestor::td/following-sibling::td")
        cluster_manager.press_esc_key(driver)
        time.sleep(1)

        cluster_manager.click_on_tab_in_vulne_page("images")
        time.sleep(1)
        
        try:
            # Wait for the table to load by checking for a known element
            WebDriverWait(driver, 15).until(
                EC.visibility_of_element_located((By.XPATH, "//td[contains(@class, 'cdk-column-workload')]//span[@uicustomtooltip]"))
            )
            logger.info("Images tab table loaded successfully.")
        except TimeoutException:
            logger.error("Images tab table did not load in time.")
            driver.save_screenshot(f"./images_tab_table_failed_to_load_{ClusterManager.get_current_timestamp()}.png")
            raise

        workload_name_1 = interaction_manager.get_text("//td[contains(@class, 'cdk-column-workload')]//span[@uicustomtooltip]")

        if workload_name == workload_name_1:
            logger.info(f"Workload name: {workload_name},the workload name are the same")
        else:    
            logger.error(f"Workload are different")
            logger.error(f"Workload name: {workload_name_1},and workload name: {workload_name},the workload name are different")

        time.sleep(1)
        cluster_manager.click_on_tab_in_vulne_page("workloads",index=1)
        time.sleep(1)
        
        risk_acceptance = RiskAcceptancePage(self._driver)
        time.sleep(3)
        risk_acceptance.navigate_to_page()
        logger.info("Navigated to risk acceptance page")
        time.sleep(1)
        risk_acceptance.switch_tab("Vulnerabilities")
        time.sleep(2)
        risk_acceptance.click_severity_element("span.medium-severity-color")
        time.sleep(2)
        risk_acceptance.click_edit_button("//armo-button[@buttontype='primary']//button[text()='Edit']")
        time.sleep(3)
        risk_acceptance.delete_ignore_rule()
        time.sleep(3)