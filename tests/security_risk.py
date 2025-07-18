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
        if self._create_cluster:
            cluster_manager.create_attack_path()

        try:
            logger.info("Running Security Risk test")
            # Only perform cluster setup if create_cluster is True
            if self._create_cluster:
                connect_cluster.click_get_started()
                connect_cluster.connect_cluster_helm()
                connect_cluster.verify_installation()
                connect_cluster.view_cluster_button()
                connect_cluster.view_connected_cluster()
                
            self.navigate_to_security_risk()
        finally:
            # Only perform cleanup if we created a cluster
            if self._create_cluster:
                self.perform_cleanup()
            logger.info("Security risk test completed")
    
    def navigate_to_security_risk(self):
        """
        Navigate to the Security Risks page, click on risk categories, apply filters, and verify results.
        """
        try:
            self.click_security_risks_menu()
            logger.info("Comparing values on the main page")
            self.compare_value("td.issues > span.font-size-14.line-height-24.armo-text-black-color", "text.total-value")
            
            # logger.info("Reset pods in the 'default' namespace...") 
            # ClusterManager.run_shell_command(self,"kubectl delete pods -n default --all")
            # logger.info("Waiting for the pods to restart...")
            # time.sleep(7)

            self.process_risk_category("Workloads", "default") 
            time.sleep(1)
            self.process_risk_category("Data", "None")
            time.sleep(1)
            self.process_risk_category("Network configuration", "default")
            time.sleep(1)
            self.process_risk_category("Attack path", "attack-suite")
            

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
        if not category_name == "Attack path":
            cluster_manager.click_close_icon_in_filter_button(category_name)
    
    def process_first_security_risk(self,category_name, namespace, before_risk):
        """
        Clicks on the first security risk and applies namespace filter.
        """
        interaction_manager = InteractionManager(self._driver)
        cluster_manager = ClusterManager(self._driver, self._wait)
        
        # logger.info("Clicking on the first security risk")
        # first_security_risk_CSS_SELECTOR = "button.armo-button.table-secondary.sm"
        # interaction_manager.click(first_security_risk_CSS_SELECTOR, by=By.CSS_SELECTOR)
        # time.sleep(1)
        
        time.sleep(5)
        # logger.info("Clicking on the first security risk")
        first_security_risk_CSS_SELECTOR = "button.armo-button.table-secondary.sm"

        # Wait until the elements are located
        first_security_risks = WebDriverWait(self._driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, first_security_risk_CSS_SELECTOR)))

        # Check if the list has at least 3 elements
        if len(first_security_risks) > 2:
            if category_name == "Workloads":
                self._driver.execute_script("arguments[0].scrollIntoView(true);", first_security_risks[3])
                logger.info("Successfully scrolled to the second security risk button.")
            else:
                self._driver.execute_script("arguments[0].scrollIntoView(true);", first_security_risks[2])
                logger.info("Successfully scrolled to the first security risk button.")        
        
            time.sleep(0.5)
            if category_name == "Workloads" or category_name == "Attack path":
                first_security_risks[3].click()
                logger.info("Successfully clicked on the second security risk button.")
            else:
                first_security_risks[2].click()
                logger.info("Successfully clicked on the first security risk button.")
        else:
            logger.error(f"Expected at least 3 elements, but found {len(first_security_risks)}.")
        
        time.sleep(2)
        # Apply Namespace filter
        cluster_manager.click_filter_button_in_sidebar_by_text(category_name=category_name, button_text="Namespace")
        time.sleep(2)
        cluster_manager.click_on_filter_checkbox_sidebar(namespace)
        time.sleep(1)
        cluster_manager.press_esc_key(self._driver)
        time.sleep(1)
        cluster_manager.press_space_key(self._driver)
        time.sleep(1)

        # Verify namespace
        if cluster_manager.get_namespace_from_element(category_name) == namespace:
            logger.info(f"Namespace {namespace} is verified") 
        else:
            logger.error(f"Namespace {namespace} is not verified")
        print("TETST")
        time.sleep(2)
        # Click on the namespace row >
        interaction_manager.click("armo-item-by-control button.armo-button.table-secondary.sm",by=By.CSS_SELECTOR)
        # time.sleep(1)
        # cluster_manager.click_button_in_namespace_row(category_name,namespace)
        print("TEST2")
        time.sleep(1)
        if category_name == "Data" or category_name == "Workloads":
            if AttachPath.compare_yaml_code_elements(self._driver, "div.row-container.yaml-code-row"):
                logger.info("SBS yamls - The number of rows is equal .")
            else:
                logger.error("SBS yamls - The number of rows is NOT equal.")
        
        if category_name == "Attack path":
            try:
                element = WebDriverWait(self._driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "td.cdk-column-baseScore .severity")))
                logger.info("Attack path page loaded")
            except TimeoutException:
                logger.error("Attack path page not loaded")
                self._driver.save_screenshot(f"./failed_to_load_attack_path_page_{ClusterManager.get_current_timestamp()}.png")
                
        # Create Risk Acceptance        
        self.create_risk_accept(self._driver, category_name)
        time.sleep(2)
        RiskAcceptancePage.navigate_to_risk_acceptance_form_sidebar(self, category_name)
    
        try:
            element = WebDriverWait(self._driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "td.cdk-column-severity .severity")))
            logger.info("Risk Acceptance page loaded")
        except TimeoutException:
            logger.error("Risk Acceptance page not loaded")
            self._driver.save_screenshot(f"./failed_to_load_risk_acceptance_page_{ClusterManager.get_current_timestamp()}.png")
                    
        if category_name == "Attack path":
            self.risk_acceptance_page()
            self.click_security_risks_menu()
        else:
            self._driver.back()
            logger.info("Navigated back to the Risk Acceptance page-1")
       
            time.sleep(2)
            
            after_risk, _ = self.compare_value("td.issues > span.font-size-14.line-height-24.armo-text-black-color", "text.total-value")
            
            if int(before_risk[0]) == int(after_risk) + 1:
                logger.info("The risk has been accepted- and the counters are correct")
            else:
                logger.error(f"The counters are incorrect: before_risk: {before_risk}, after_risk: {after_risk}") 

            self.risk_acceptance_page()

            self._driver.back()
            logger.info("Navigated back to the Risk Acceptance page-2")
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
    
    def create_risk_accept(self, driver, category_name):

        risk_accept = IgnoreRule(driver)
        if category_name == "Attack path":
            risk_accept.click_ignore_on_from_attach_path()
        else:
            risk_accept.click_ignore_rule_button_sidebar()

        time.sleep(1)
        container_name = risk_accept.get_ignore_rule_field(2)
        logger.info(f"Container name: {container_name}")
        time.sleep(1.5)
        if category_name == "Attack path":
            risk_accept.save_ignore_rule()
        else:
            risk_accept.click_save_button_sidebar()
    
    def risk_acceptance_page(self):
        risk_acceptance = RiskAcceptancePage(self._driver)
        risk_acceptance.navigate_to_page()
        risk_acceptance.click_severity_element("td.mat-mdc-cell.cdk-column-severity")
        time.sleep(1)
        risk_acceptance.click_edit_button("//button[contains(text(), 'Edit')]")
        time.sleep(2.5)
        risk_acceptance.delete_ignore_rule()
        time.sleep(3)

