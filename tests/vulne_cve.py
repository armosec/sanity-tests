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
        logger.info("Vulne CVE test")
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
        time.sleep(1)
        cluster_manager.click_on_filter_ckackbox("default")
        time.sleep(1)
        cluster_manager.press_esc_key(driver)
        time.sleep(1)
        cluster_manager.click_filter_button("Workload")
        time.sleep(1)
        cluster_manager.click_on_filter_ckackbox("alpine-deployment")        
        time.sleep(1)
        cluster_manager.press_esc_key(driver)
        time.sleep(1)   
        cluster_manager.click_filter_button("In Use")
        time.sleep(0.5)
        yes_inUse_xpath = "//li[contains(@class, 'd-flex align-items-center') and .//span[text()='Yes']]"
        interaction_manager.click(yes_inUse_xpath, By.XPATH)
        cluster_manager.press_esc_key(driver)
        time.sleep(1)
        cluster_manager.click_filter_button("Severity")
        time.sleep(1)
        cluster_manager.click_on_filter_ckackbox("Medium") 
        cluster_manager.press_esc_key(driver)       
        time.sleep(1)
        
        ignore_rule = IgnoreRule(driver)
        ignore_rule.click_ignore_button()
        logger.info("Clicked on the 'Accept Risk' button")
        time.sleep(1)
        ignore_rule.save_ignore_rule()
        