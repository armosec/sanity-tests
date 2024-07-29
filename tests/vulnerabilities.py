import time
import logging
from .base_test import BaseTest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from .cluster_operator import ClusterManager, IgnoreRule, ConnectCluster

logger = logging.getLogger(__name__)

class Vulnerabilities(BaseTest):
    def run(self):
        connect_cluster = ConnectCluster(self._driver)
        cluster_manager = ClusterManager(self._driver)
        cluster_manager.create_attack_path()  
        login_url = self.get_login_url()
        self.login(login_url)
        try:
            connect_cluster.click_get_started()
            connect_cluster.connect_cluster_helm()
            connect_cluster.verify_installation()
            connect_cluster.view_cluster_button()
            connect_cluster.view_connected_cluster()
            self.navigate_to_vulnerabilities()
        finally:
            self.perform_cleanup()  
            logger.info("Cleanup completed successfully")

    def navigate_to_vulnerabilities(self):
        driver = self._driver
        interaction_manager = self._interaction_manager
        
        try:
            interaction_manager.click('image-scanning-left-menu-item', By.ID)
            logger.info("Vulnerabilities clicked")
        except:
            logger.error("Failed to click on vulnerabilities")
            driver.save_screenshot(f"./failed_to_click_on_vulnerabilities_{ClusterManager.get_current_timestamp()}.png")
        
        cluster_manager = ClusterManager(driver)
        try:
            cluster_manager.click_on_vuln_view_button("Workloads")
        except Exception as e:
            logger.error(f"Failed to click on vuln view button or menu item: {e}")
            driver.save_screenshot(f"./failed_to_click_vuln_view_or_menu_item_{ClusterManager.get_current_timestamp()}.png")

        try:
            name_space = interaction_manager.wait_until_exists('/html/body/armo-root/div/div/div/armo-workloads-page/div[2]/armo-table-filters/armo-created-filters-list/div/armo-multi-select-filter[2]/armo-common-trigger-button/armo-button/button', By.XPATH)
            name_space.click()
            logger.info("Namespace filter clicked")
        except:
            logger.error("Failed to click on namespace filter")
            driver.save_screenshot(f"./failed_to_click_on_namespace_filter_{ClusterManager.get_current_timestamp()}.png")
        
        try:
            select_all_button = interaction_manager.wait_until_exists("//span[contains(@class, 'color-blue') and contains(text(), 'Select all')]", By.XPATH)
            driver.execute_script("arguments[0].click();", select_all_button)
            logger.info("All namespaces selected")
        except:
            logger.error("Failed to select all namespaces")
            driver.save_screenshot(f"./failed_to_select_all_namespaces_{ClusterManager.get_current_timestamp()}.png")

        time.sleep(2)
        
        try:
            checkboxes_container_xpath = '//ul[@class="m-0 px-0 pt-1 font-size-14"]'
            checkboxes_container = interaction_manager.wait_until_exists(checkboxes_container_xpath, By.XPATH)
            checkbox_elements = checkboxes_container.find_elements(By.XPATH, ".//mat-checkbox")
            selected_checkbox_names = []

            for checkbox_element in checkbox_elements:
                checkbox = checkbox_element.find_element(By.XPATH, ".//input[@type='checkbox']")
                if checkbox.is_selected():
                    label_span = checkbox_element.find_element(By.XPATH, ".//span[@class='mat-tooltip-trigger value truncate']")
                    label_text = label_span.text.strip()
                    if label_text:
                        selected_checkbox_names.append(label_text)
                    else:
                        label_text = label_span.get_attribute('aria-describedby')
                        if label_text:
                            tooltip_text = label_span.get_attribute('aria-label') or label_span.get_attribute('title')
                            selected_checkbox_names.append(tooltip_text)
            logger.info(f"Selected checkboxes: {selected_checkbox_names}")
        except:
            logger.error("Failed to verify selected checkboxes")
            driver.save_screenshot(f"./failed_to_verify_selected_checkboxes_{ClusterManager.get_current_timestamp()}.png")

        try:
            clear_button = interaction_manager.wait_until_exists("//span[contains(@class, 'color-blue') and contains(@class, 'font-size-12') and contains(text(), 'Clear')]", By.XPATH)
            clear_button.click()
            logger.info("All checkboxes cleared")
        except:
            logger.error("Failed to click clear button")
            driver.save_screenshot(f"./failed_to_click_clear_button_{ClusterManager.get_current_timestamp()}.png")
        
        time.sleep(1)
        
        try:
            checkboxes_container = interaction_manager.wait_until_exists(checkboxes_container_xpath, By.XPATH)
            checkboxes = checkboxes_container.find_elements(By.XPATH, ".//mat-checkbox//input[@type='checkbox']")
            none_selected = all(not checkbox.is_selected() for checkbox in checkboxes)
            logger.info(f"All checkboxes unselected: {none_selected}")
        except:
            logger.error("Failed to verify unselected checkboxes")
            driver.save_screenshot(f"./failed_to_verify_unselected_checkboxes_{ClusterManager.get_current_timestamp()}.png")

        ClusterManager.press_esc_key(driver)

        try:
            name_space = interaction_manager.wait_until_exists('/html/body/armo-root/div/div/div/armo-workloads-page/div[2]/armo-table-filters/armo-created-filters-list/div/armo-multi-select-filter[2]/armo-common-trigger-button/armo-button/button', By.XPATH)
            name_space.click()
            logger.info("Namespace filter clicked")
        except:
            logger.error("Failed to click on namespace filter")
            driver.save_screenshot(f"./failed_to_click_on_namespace_filter_{ClusterManager.get_current_timestamp()}.png")

        try:
            checkbox_label_xpath = "//span[contains(@class, 'mat-checkbox-label') and .//span[contains(text(), 'default')]]"
            checkbox_label = interaction_manager.wait_until_exists(checkbox_label_xpath, By.XPATH)
            time.sleep(0.5)
            checkbox_label.click()
            logger.info("Namespace selected: default")
        except:
            logger.error("Failed to select the namespace")
            driver.save_screenshot(f"./failed_to_select_the_namespace_{ClusterManager.get_current_timestamp()}.png")

        ClusterManager.press_esc_key(driver)
        time.sleep(1)

        try:
            severity_filter_elements = driver.find_elements(By.XPATH, "//div[@class='severity-background']")
            severity_filter_elements[2].click()
            logger.info("Clicked on the medium severity filter")
        except Exception as e:
            logger.error(f"Failed to click on the medium severity filter: {str(e)}")
            driver.save_screenshot(f"./failed_to_click_on_medium_severity_filter_{ClusterManager.get_current_timestamp()}.png")

        time.sleep(1)
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
