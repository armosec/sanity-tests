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
            
            # Process each category with refresh between them           
            self.process_risk_category("Attack path", "attack-suite")
            self.reset_page_for_next_category()
            
            self.process_risk_category("Workloads", "default")
            self.reset_page_for_next_category()
        
            self.process_risk_category("Data", "None")
            self.reset_page_for_next_category()
            
            self.process_risk_category("Network configuration", "default")

        except Exception as e:
            logger.error(f"Error navigating in security risk page: {e}")

    def reset_page_for_next_category(self):
        """
        Resets the page state by refreshing and navigating back to Security Risks.
        This ensures Angular is in a clean state for the next category.
        """
        try:
            logger.info("=" * 60)
            logger.info("Resetting page for next category...")
            logger.info("=" * 60)
            time.sleep(1)
            ClusterManager.click_clear_button(self._driver)
            time.sleep(1)
            # Full page refresh
            self._driver.refresh()
            time.sleep(5)  # Wait for page to reload
            
            # Wait for page to be interactive
            WebDriverWait(self._driver, 20).until(
                EC.element_to_be_clickable((By.ID, "security-risks-left-menu-item"))
            )
            logger.info("Page refreshed successfully")
            
            # Navigate back to Security Risks
            self.click_security_risks_menu()
            time.sleep(3)
            
            # Wait for category buttons to be ready
            WebDriverWait(self._driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Attack path')]"))
            )
            logger.info("Ready for next category")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Failed to reset page: {e}")
            self._driver.save_screenshot(f"./failed_to_reset_page_{ClusterManager.get_current_timestamp()}.png")
            raise
    
    def process_risk_category(self, category_name, namespace):
        """
        Processes a given risk category by selecting the category, comparing values, applying filters, and verifying namespace.
        """
        cluster_manager = ClusterManager(self._driver, self._wait)
        logger.info(f"###______Processing Risk Category:  {category_name} ______###")
        
        # 1. Open category and get risk count
        cluster_manager.click_button_by_text(category_name)
        time.sleep(2)
        before_risk, _ = self.compare_value("td.issues > span.font-size-14.line-height-24.armo-text-black-color", "text.total-value")
        
        # 2. Click on the correct security risk button to open sidebar
        time.sleep(5)

        # Wait for any loading indicators to disappear
        try:
            WebDriverWait(self._driver, 10).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, "armo-loader, .loading-spinner, .spinner"))
            )
            logger.info("Loading indicator disappeared")
        except:
            pass  # No loader found, that's fine

        first_security_risk_CSS_SELECTOR = "button.armo-button.table-secondary.sm"
        first_security_risks = WebDriverWait(self._driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, first_security_risk_CSS_SELECTOR)))

        if category_name == "Workloads" or category_name == "Attack path":
            required_index = 3
        else:
            required_index = 2

        if len(first_security_risks) > required_index:
            button_to_click = first_security_risks[required_index]
            
            # Scroll button into view
            self._driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button_to_click)
            time.sleep(1)
            
            # Try regular click first, fallback to JS click
            try:
                button_to_click.click()
                logger.info(f"Successfully clicked security risk button (index {required_index}) with regular click")
            except Exception as click_error:
                logger.warning(f"Regular click failed ({str(click_error)[:100]}), using JS click")
                self._driver.execute_script("arguments[0].click();", button_to_click)
                logger.info(f"Successfully clicked security risk button (index {required_index}) with JS click")
        else:
            logger.error(f"Expected at least {required_index + 1} elements, but found {len(first_security_risks)}.")
        
        # 3. Wait for sidebar to appear
        time.sleep(3.5)
        try:
            WebDriverWait(self._driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.cdk-overlay-pane"))
            )
            logger.info("Sidebar overlay is present")
        except Exception as e:
            logger.error(f"Sidebar overlay not found: {str(e)}")
            self._driver.save_screenshot(f"./sidebar_overlay_not_found_{ClusterManager.get_current_timestamp()}.png")
        
        
        if category_name != "Attack path" and category_name != "Network configuration":
            cluster_manager.click_filter_button_in_sidebar_by_text(category_name=category_name, button_text="Namespace")
            time.sleep(2)
            cluster_manager.click_on_filter_checkbox_sidebar(namespace)
            time.sleep(1)
            
            # Close the dropdown - try ESC multiple times
            for _ in range(3):
                cluster_manager.press_esc_key(self._driver)
                time.sleep(0.5)
            
            # FORCE CLOSE: Remove all overlay backdrops with JavaScript
            try:
                self._driver.execute_script("""
                    // Remove all dropdown overlays and backdrops
                    const backdrops = document.querySelectorAll('.cdk-overlay-backdrop');
                    backdrops.forEach(b => b.remove());
                    
                    const overlays = document.querySelectorAll('.cdk-overlay-pane');
                    overlays.forEach(overlay => {
                        // Only remove dropdown overlays, not the main sidebar
                        if (overlay.querySelector('.mat-mdc-menu-panel')) {
                            overlay.remove();
                        }
                    });
                """)
                logger.info("Forcefully removed dropdown overlays")
            except Exception as e:
                logger.warning(f"Could not remove overlays: {e}")
            
            time.sleep(2)  
        
        # 4. Click button in namespace row to open detailed view
        cluster_manager.click_button_in_namespace_row(category_name, namespace)
        time.sleep(2)

        # 5. Compare YAML for Data/Workloads
        if category_name == "Data" or category_name == "Workloads":
            if AttachPath.compare_yaml_code_elements(self._driver, "div.row-container.yaml-code-row"):
                logger.info("SBS yamls - The number of rows is equal .")
            else:
                logger.error("SBS yamls - The number of rows is NOT equal.")

        # 6. Verify Attack path page loaded
        if category_name == "Attack path":
            try:
                element = WebDriverWait(self._driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "td.cdk-column-baseScore .severity")))
                logger.info("Attack path page loaded")
            except TimeoutException:
                logger.error("Attack path page not loaded")
                self._driver.save_screenshot(f"./failed_to_load_attack_path_page_{ClusterManager.get_current_timestamp()}.png")

        # 7. Create risk acceptance
        time.sleep(2)
        self.create_risk_accept(self._driver, category_name)
        time.sleep(2)

        # 8. Navigate to Risk Acceptance page
        RiskAcceptancePage.navigate_to_risk_acceptance_form_sidebar(self, category_name)

        try:
            element = WebDriverWait(self._driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "td.cdk-column-severity .severity")))
            logger.info("Risk Acceptance page loaded")
        except TimeoutException:
            logger.error("Risk Acceptance page not loaded")
            self._driver.save_screenshot(f"./failed_to_load_risk_acceptance_page_{ClusterManager.get_current_timestamp()}.png")

        # 9. Navigate back and verify counters
        if category_name == "Attack path":
            self.risk_acceptance_page()
            self.click_security_risks_menu()
        else:
            self._driver.back()
            logger.info("Navigated back to the main Security Risks page after risk acceptance")
            
            # Clean up any stale overlays after navigation
            try:
                self._driver.execute_script("""
                    document.querySelectorAll('div.cdk-overlay-pane, .cdk-overlay-backdrop').forEach(el => el.remove());
                """)
            except:
                pass
            
            time.sleep(2)
            
            # Verify counter after accepting risk
            after_risk, _ = self.compare_value("td.issues > span.font-size-14.line-height-24.armo-text-black-color", "text.total-value")
            
            if int(before_risk) == int(after_risk) + 1:
                logger.info("The risk has been accepted - counters are correct")
            else:
                logger.error(f"The counters are incorrect: before_risk: {before_risk}, after_risk: {after_risk}") 

            # Now delete the risk acceptance to verify counter goes back up
            self.risk_acceptance_page()

            self._driver.back()
            logger.info("Navigated back after deleting risk acceptance")
            time.sleep(2)
            
            after_delete_risk, _ = self.compare_value("td.issues > span.font-size-14.line-height-24.armo-text-black-color", "text.total-value")

            if int(after_delete_risk) == int(after_risk) + 1:
                logger.info("The risk has been revoked - counters are correct")
            else:
                logger.error(f"The counters are incorrect: after_risk: {after_risk}, after_delete_risk: {after_delete_risk}")
        
        
    def click_security_risks_menu(self):  # ← Make sure this exists!
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
        time.sleep(4)

        if category_name == "Attack path":
            risk_accept.click_ignore_on_from_attach_path()
        else:
            risk_accept.click_ignore_rule_button_sidebar()

        time.sleep(4)
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

