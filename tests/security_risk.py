import time
import logging
from .base_test import BaseTest
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from .cluster_operator import ClusterManager, IgnoreRule, RiskAcceptancePage , ConnectCluster
from .interaction_manager import InteractionManager
from tests.attach_path import AttachPath

logger = logging.getLogger(__name__)

class SecurityRisk(BaseTest):
    
    def run(self):
        # Initialize ClusterManager and ConnectCluster objects
        cluster_manager = ClusterManager(self._driver, self._wait)
        connect_cluster = ConnectCluster(self._driver, self._wait)

        # Log in to the system
        login_url = self.get_login_url()
        self.login(login_url)
        cluster_manager.create_attack_path()

        try:
            logger.info("Running Security Risk test")
            connect_cluster.click_get_started()
            connect_cluster.connect_cluster_helm()
            connect_cluster.verify_installation()
            connect_cluster.view_cluster_button()
            connect_cluster.view_connected_cluster()
            self.navigate_to_security_risk()
        finally:
            # self.perform_cleanup()  
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
            self.process_risk_category("Data", "None")
            time.sleep(1)
            self.process_risk_category("Network configuration", "default")
            time.sleep(1)
            # self.process_risk_category("Attack path", "default")

        except Exception as e:
            logger.error(f"Error navigating in security risk page: {e}")
    
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
        before_risk, _ = self.compare_value("td.issues > span.font-size-14.line-height-24.armo-text-black-color", "text.total-value")
        
        # Click on the first security risk and apply filters
        self.process_first_security_risk(category_name, namespace , before_risk)
        
        # Close the filter
        cluster_manager.click_close_icon_in_filter_button(category_name)
    
    def process_first_security_risk(self,category_name, namespace, before_risk):
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
        cluster_manager.click_filter_button_in_sidebar_by_text(category_name=category_name, button_text="Namespace")
        time.sleep(1)
        cluster_manager.click_on_filter_ckackbox_filter(namespace)
        time.sleep(1)
        cluster_manager.press_esc_key(self._driver)
        time.sleep(1)
        # Verify namespace
        if cluster_manager.get_namespace_from_element(category_name) == namespace:
            logger.info(f"Namespace {namespace} is verified") 
        else:
            logger.error(f"Namespace {namespace} is not verified")
        time.sleep(1)
        cluster_manager.click_button_in_namespace_row(category_name,namespace)
        time.sleep(1)
        if category_name == "Data" or category_name == "Workloads":
            if AttachPath.compare_yaml_code_elements(self._driver, "div.row-container.yaml-code-row"):
                logger.info("SBS yamls - The number of rows is equal .")
            else:
                logger.error("SBS yamls - The number of rows is NOT equal.")
                
        # Create Risk Accep
        self.create_risk_accept(self._driver)
        time.sleep(2)
        RiskAcceptancePage.navigate_to_risk_acceptance_form_sidebar(self)
    
        try:
            element = WebDriverWait(self._driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "td.mat-cell.cdk-cell.cdk-column-name.mat-column-name")))
            logger.info("Risk Acceptance page loaded")
        except TimeoutException:
            logger.error("Risk Acceptance page not loaded")
            self._driver.save_screenshot(f"./failed_to_load_risk_acceptance_page_{ClusterManager.get_current_timestamp()}.png")
                    
        self._driver.back()
        logger.info("Navigated back to the Risk Acceptance page")
        time.sleep(2)
        after_risk, _ = self.compare_value("td.issues > span.font-size-14.line-height-24.armo-text-black-color", "text.total-value")
        
        if int(before_risk[0]) == int(after_risk) + 1:
            logger.info("The risk has been accepted- and the counters are correct")
        else:
            logger.error(f"The counters are incorrect: before_risk: {before_risk}, after_risk: {after_risk}") 
                       
        self.risk_acceptance_page()
        self._driver.back()
        logger.info("Navigated back to the Risk Acceptance page")
        time.sleep(2)
        
        after__delete_risk, _ = self.compare_value("td.issues > span.font-size-14.line-height-24.armo-text-black-color", "text.total-value")
        
        if int(after__delete_risk[0]) == int(after_risk) + 1:
            logger.info("The risk has been accepted- and the counters are correct")
        else:
            logger.error(f"The counters are incorrect: before_delete_risk: {before_risk}, after_delete_risk: {after_risk}") 
        
    
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
        
        return text1, text2
            
    def create_risk_accept(self, driver):
        risk_accept = IgnoreRule(driver)
        risk_accept.click_ignore_rule_button_sidebar()
        logger.info("Clicked on the 'Accept Risk' button")
        time.sleep(1)
        container_name=risk_accept.get_ignore_rule_field(2)
        logger.info(f"Container name: {container_name}")
        time.sleep(1.5)
        risk_accept.click_save_button_sidebar()
        # return container_name
    
    def risk_acceptance_page(self):
        risk_acceptance = RiskAcceptancePage(self._driver)
        risk_acceptance.navigate_to_page()
        risk_acceptance.click_severity_element("td.mat-cell.cdk-cell.cdk-column-severity.mat-column-severity.ng-star-inserted")
        time.sleep(1)
        risk_acceptance.click_edit_button("//button[contains(text(), 'Edit')]")
        time.sleep(2.5)
        risk_acceptance.delete_ignore_rule()
        time.sleep(3)

