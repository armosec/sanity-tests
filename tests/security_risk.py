import time
import logging
import json
from .base_test import BaseTest
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from .cluster_operator import ClusterManager, IgnoreRule, RiskAcceptancePage , ConnectCluster
from .interaction_manager import InteractionManager

logger = logging.getLogger(__name__)

class SecurityRisk(BaseTest):
    def run(self):
        connect_cluster = ConnectCluster(self._driver, self._wait)
        connect_maneger = ClusterManager(self._driver, self._wait)
        # connect_maneger.create_attack_path()
        login_url = self.get_login_url()
        self.login(login_url)
        try:
            logger.info("Running Security risk test")
            # connect_cluster.click_get_started()
            # connect_cluster.connect_cluster_helm()
            # connect_cluster.verify_installation()
            # connect_cluster.view_cluster_button()
            # connect_cluster.view_connected_cluster()
            self.navigate_to_security_risk()
        finally:
            # self.perform_cleanup()
            logger.info("Security risk test completed")
            
    def navigate_to_security_risk(self):
        driver = self._driver
        wait = self._wait
        cluster_manager = ClusterManager(driver, wait)
        interaction_manager = InteractionManager(driver)
        try:
            interaction_manager.click("security-risks-left-menu-item", by=By.ID)
            logger.info("Security Risks page clicked")
        except Exception as e:
            logger.error(f"Failed to click on Security Risks page: {e}")
            driver.save_screenshot(f"./failed_to_click_on_security_risks_page_{ClusterManager.get_current_timestamp()}.png")
    
        # total_issues_number_1 = interaction_manager.get_text("td.issues > span.font-size-14.line-height-24.armo-text-black-color", by=By.CSS_SELECTOR)
        # total_issues_number_2 = interaction_manager.get_text("text.total-value", by=By.CSS_SELECTOR)
        # # Compare the two values
        # if total_issues_number_1 == total_issues_number_2:
        #     print(f"The values are the same: {total_issues_number_1}")
        # else:
        #     print(f"The values are different: {total_issues_number_1} vs {total_issues_number_2}")
        
        self.compare_value("td.issues > span.font-size-14.line-height-24.armo-text-black-color", "text.total-value")
        time.sleep(2) # Wait for 5 seconds - test 
        
        cluster_manager.click_button_by_text("Workloads")
        time.sleep(1) # Wait for 5 seconds - test
        self.compare_value("td.issues > span.font-size-14.line-height-24.armo-text-black-color", "text.total-value")
        time.sleep(1)
        cluster_manager.close_filter_by_type("Workloads")
  
        time.sleep(10)
        
        
    def compare_value(self, css_selector1: str, css_selector2: str):
        interaction_manager = self._interaction_manager

        text1 = interaction_manager.get_text(css_selector1, by=By.CSS_SELECTOR)
        text2 = interaction_manager.get_text(css_selector2, by=By.CSS_SELECTOR)

        if text1 == text2:
            logger.info(f"The values are the same: {text1}")
        else:
            logger.error(f"The values are different: {text1} vs {text2}")
        
        
        
        
    