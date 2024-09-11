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
        # Initialize ClusterManager and ConnectCluster objects
        cluster_manager = ClusterManager(self._driver, self._wait)
        connect_cluster = ConnectCluster(self._driver, self._wait)

        # Log in to the system
        login_url = self.get_login_url()
        self.login(login_url)

        try:
            logger.info("Running Security Risk test")
            self.navigate_to_security_risk()
        finally:
            logger.info("Security risk test completed")
    
    def navigate_to_security_risk(self):
        """
        Navigate to the Security Risks page, click on risk categories, apply filters, and verify results.
        """
        try:
            self.click_security_risks_menu()
            logger.info("Comparing values on the main page")
            self.compare_value("td.issues > span.font-size-14.line-height-24.armo-text-black-color", "text.total-value")
            
            # Process the 'Workloads' risk category
            self.process_risk_category("Workloads", "default")
            time.sleep(1)
            # Process the 'Data' risk category
            self.process_risk_category("Data", "None")

        except Exception as e:
            logger.error(f"Error navigating security risk: {e}")
    
    def click_security_risks_menu(self):
        """
        Clicks on the Security Risks left menu item.
        """
        interaction_manager = InteractionManager(self._driver)
        try:
            interaction_manager.click("security-risks-left-menu-item", by=By.ID)
            logger.info("Security Risks page clicked")
        except Exception as e:
            logger.error(f"Failed to click on Security Risks page: {e}")
            self._driver.save_screenshot(f"./failed_to_click_on_security_risks_page_{ClusterManager.get_current_timestamp()}.png")
    
    def process_risk_category(self, category_name, namespace):
        """
        Processes a given risk category by selecting the category, comparing values, applying filters, and verifying namespace.
        """
        cluster_manager = ClusterManager(self._driver, self._wait)
        logger.info(f"Processing Risk Category: {category_name}")
        cluster_manager.click_button_by_text(category_name)
        
        # Compare values on the page
        time.sleep(1)
        self.compare_value("td.issues > span.font-size-14.line-height-24.armo-text-black-color", "text.total-value")
        
        # Click on the first security risk and apply filters
        self.process_first_security_risk(cluster_manager, namespace)
        
        # Close the filter
        cluster_manager.click_close_icon_in_filter_button(category_name)
    
    def process_first_security_risk(self, cluster_manager, namespace):
        """
        Clicks on the first security risk and applies namespace filter.
        """
        interaction_manager = InteractionManager(self._driver)
        cluster_manager = ClusterManager(self._driver, self._wait)
        
        logger.info("Clicking on the first security risk")
        first_security_risk_CSS_SELECTOR = "button.armo-button.table-secondary.sm"
        interaction_manager.click(first_security_risk_CSS_SELECTOR, by=By.CSS_SELECTOR)
        time.sleep(1)
        
        # Apply Namespace filter
        cluster_manager.click_filter_button_in_sidebar_by_text("Namespace")
        time.sleep(1)
        cluster_manager.click_on_filter_ckackbox_filter(namespace)
        cluster_manager.press_esc_key(self._driver)
        time.sleep(1)
        
        # Verify namespace
        cluster_manager.verify_namespace_and_click_button(namespace)
        time.sleep(6)
        cluster_manager.press_esc_key(self._driver)
    
    def compare_value(self, css_selector1: str, css_selector2: str):
        """
        Compares two values on the page based on their CSS selectors.
        """
        interaction_manager = InteractionManager(self._driver)
        
        text1 = interaction_manager.get_text(css_selector1, by=By.CSS_SELECTOR)
        text2 = interaction_manager.get_text(css_selector2, by=By.CSS_SELECTOR)
        if text1 == text2:
            logger.info(f"The values are the same: {text1}")
        else:
            logger.error(f"The values are different: {text1} vs {text2}")

