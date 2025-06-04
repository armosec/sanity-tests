import time
import logging
from .base_test import BaseTest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from .cluster_operator import ClusterManager, IgnoreRule, ConnectCluster, RiskAcceptancePage
from .vulne_cve import VulneCvePage

logger = logging.getLogger(__name__)

class Vulnerabilities(BaseTest):
    def run(self):
        connect_cluster = ConnectCluster(self._driver, self._wait)
        cluster_manager = ClusterManager(self._driver, self._wait)
        # cluster_manager.create_attack_path()  
        login_url = self.get_login_url()
        self.login(login_url)
        try:
            interact = self._interaction_manager
            interact.click('image-scanning-left-menu-item', By.ID)  # Click on vulnerabilities page
            
            # Only perform cluster setup if create_cluster is True
            if self._create_cluster:
                connect_cluster.click_get_started()
                connect_cluster.connect_cluster_helm()
                connect_cluster.verify_installation()
                connect_cluster.view_cluster_button()
                connect_cluster.view_connected_cluster()
                cluster_manager.create_attack_path()
                print("Wait for 30 seconds")
                time.sleep(30)
                
            self.run_vulne_cve_test()
            self.navigate_to_vulnerabilities()
            self.risk_acceptance_page()
            print("Running vulnerabilities test")
        finally:
            # Only perform cleanup if we created a cluster
            if self._create_cluster:
                self.perform_cleanup()
            logger.info("Test completed successfully")

    def navigate_to_vulnerabilities(self):
        driver = self._driver
        interaction_manager = self._interaction_manager
        cluster_manager = ClusterManager(self._driver, self._wait)
        
        try:
            interaction_manager.click('image-scanning-left-menu-item', By.ID)
            logger.info("Vulnerabilities clicked")
        except:
            logger.error("Failed to click on vulnerabilities")
            driver.save_screenshot(f"./failed_to_click_on_vulnerabilities_{ClusterManager.get_current_timestamp()}.png")
        
        try:
            cluster_manager.click_on_vuln_view_button("Workloads")
        except Exception as e:
            logger.error(f"Failed to click on vuln view button or menu item: {e}")
            driver.save_screenshot(f"./failed_to_click_vuln_view_or_menu_item_{ClusterManager.get_current_timestamp()}.png")
        
        time.sleep(1)
        cluster_manager.click_filter_button("Workload")
            
        # click on the select all button
        try:
            time.sleep(1)
            select_all_button = interaction_manager.wait_until_exists("//span[contains(text(), 'Select all')]", By.XPATH)
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
                    label_span = checkbox_element.find_element(By.XPATH, ".//span[contains(@class, 'tooltip-trigger') and contains(@class, 'value')]")
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
            
        # click on the clear button
        try:
            time.sleep(1)
            clear_button_xpath = "//span[contains(text(), 'Clear')]"
            clear_button = interaction_manager.wait_until_exists(clear_button_xpath, By.XPATH)

            # Scroll into view and click with JS to avoid overlay issues
            self._driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", clear_button)
            time.sleep(0.3)  # allow animations to finish
            self._driver.execute_script("arguments[0].click();", clear_button)
            logger.info("All checkboxes cleared using JS click")
        except Exception as e:
            logger.error(f"Failed to click clear button: {str(e)}")
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
        time.sleep(1)
        ClusterManager.press_space_key(driver)
        time.sleep(1)
        cluster_manager.click_filter_button("Namespace")
        time.sleep(1)
        cluster_manager.click_checkbox_by_name("default")
        time.sleep(1)
        # ClusterManager.click_close_filter(driver)
        ClusterManager.press_esc_key(driver)
        time.sleep(1)
        ClusterManager.press_space_key(driver)
        time.sleep(1)
        # click on the high severity filter in the first row
        try:
            wait = WebDriverWait(driver, 10)
            wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='severity-background']"))) # Wait for the element to be clickable
            # Find the element using XPath
            driver.find_elements(By.XPATH, "//div[@class='severity-background']")[1].click()
            logger.info("Clicked on the high severity filter")

        except Exception as e:
            logger.error(f"Failed to click on the high severity filter: {str(e)}")
            driver.save_screenshot(f"./failed_to_click_on_high_severity_filter_{ClusterManager.get_current_timestamp()}.png")
        time.sleep(1)
        
        # try:
        #     WebDriverWait(self._driver, 20).until(
        #         EC.presence_of_element_located((By.CSS_SELECTOR, "tr[role='row']"))
        #     )
        #     self._driver.find_elements(By.CSS_SELECTOR, "tr[role='row']")[1].click()
        #     logger.info("Clicked on the first row in the table")
        # except Exception as e:
        #     logger.error(f"Failed to click on first row: {str(e)}")
        #     driver.save_screenshot(f"./failed_to_click_first_row_{ClusterManager.get_current_timestamp()}.png")

            
        num_of_high_cve = interaction_manager.count_rows()
        logger.info(f"Number of high CVEs: {num_of_high_cve}")
        # driver.save_screenshot(f"./number_of_high_cves_{ClusterManager.get_current_timestamp()}.png")

        try:
            time.sleep(1)            
            # Wait for the first row to be clickable (to ensure the table is loaded)
            xpath = "(//tbody[@role='rowgroup']//td[contains(@class,'cdk-column-name')]//a)[1]"
            link = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))

            # Scroll and force-click via JavaScript
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", link)
            driver.execute_script("arguments[0].click();", link)
            logger.info("Successfully clicked on the firs CVE.")
        except Exception as e:
                logger.error(f"Failed to click on the first CVE: {e}")
                driver.save_screenshot("./failed_to_click_cve.png")
        
        time.sleep(1)  
        # this is a referecne click - in this way we can click on the Runtime Analysis 
        tab_element = WebDriverWait(self._driver, 20).until(
                EC.visibility_of_element_located((By.XPATH, "//span[@class='mdc-tab__text-label' and text()='Threat Intelligence']")))  
        tab_element.click() 
        time.sleep(1) 
        cluster_manager.click_tab_on_sidebar(tab_name='Runtime Analysis')
        time.sleep(2)
        try:
            image_tag = interaction_manager.get_text("//span[contains(text(), 'docker.io/library/alpine')]")
            if image_tag == "docker.io/library/alpine:3.18.2":
                logger.info("Image tag is verified")
            else:    
                logger.error("Failed - Image tag is not verified")
                driver.save_screenshot(f"./failed_to_verify_image_tag_{ClusterManager.get_current_timestamp()}.png")
        except:
            logger.error("Failed to get image tag")
            driver.save_screenshot(f"./failed_to_get_image_tag_{ClusterManager.get_current_timestamp()}.png")
        
        # click on the bottom ">" in the saide panel
        cluster_manager.click_overlay_button()
        time.sleep(1)
        workload_name = interaction_manager.get_text("(//td[contains(@class, 'cdk-column-value')])[1]")
        ClusterManager.press_esc_key(driver)
        
        
        
        time.sleep(1)
        ignore_rule = IgnoreRule(driver)
        ignore_rule.click_ignore_button()
        logger.info("Clicked on the 'Accept Risk' button")
        
        # not working because JS click on risk acceptance button
        # time.sleep(3)
        # workload_name_from_ignore_rule_modal = ignore_rule.get_ignore_rule_field(2).strip().lower()
        # expected_value = workload_name.strip().lower()

        # logger.info(f"The workload name: {workload_name_from_ignore_rule_modal}")

        # if workload_name_from_ignore_rule_modal == expected_value:
        #     logger.info("Workload name is verified")
        # else:
        #     logger.error("Workload name is not verified")
        #     logger.error(f"The workload we get: '{workload_name_from_ignore_rule_modal}', and expected to: '{expected_value}'")
     
        print("waiting for the ignore rule modal to appear")
        time.sleep(5)

        ignore_rule.save_ignore_rule() 
        time.sleep(2)
        ignore_rule.igor_rule_icon_check()
        #need to rescane to check this
        # num_of_high_cve_after_risk_accept = interaction_manager.count_rows()
        # if (num_of_high_cve - 2)== num_of_high_cve_after_risk_accept:
        #     logger.info("Risk acceptance is successful- The number of high CVEs is reduced by 2")
        # else:
        #     logger.error(f"Failed - Risk acceptance is not successful. The number of high CVEs is not reduced by 2.\n"
        #                 f"Actual: {num_of_high_cve_after_risk_accept}\n"
        #                 f"Expected: {num_of_high_cve - 2}")
                         
        #     driver.save_screenshot(f"./failed_risk_acceptance_{ClusterManager.get_current_timestamp()}.png")


        cluster_manager.click_on_tab_in_vulne_page("details")
        time.sleep(1)
        
        workload_name_from_details = cluster_manager.get_value_by_label("NAME")
        if workload_name.lower().strip() == workload_name_from_details.lower().strip():
            logger.info("Workload name is verified")
        else:    
            logger.error("Workload name is not verified")
            logger.error(f"workload name : {workload_name_from_details},and workload name: {workload_name},the workload name are different")
            
        cluster_manager.click_on_tab_in_vulne_page("images")
        image_tag_1 = interaction_manager.get_text("(//button[@class='armo-button tertiary sm'])[1]")
        if image_tag == image_tag_1:
            logger.info("Image tag is verified")
        else:    
            logger.error("Image tag is not verified")
            driver.save_screenshot(f"./failed_to_verify_image_tag_{ClusterManager.get_current_timestamp()}.png")

    def run_vulne_cve_test(self):
        VulneCvePage.vulne_cve_test(self)            
    
    def risk_acceptance_page(self):
        risk_acceptance = RiskAcceptancePage(self._driver)
        time.sleep(3)
        risk_acceptance.navigate_to_page()
        logger.info("Navigated to risk acceptance page")
        time.sleep(1)
        risk_acceptance.switch_tab("Vulnerabilities")
        risk_acceptance.click_severity_element("td.mat-mdc-cell span.high-severity-color")
        time.sleep(2)
        risk_acceptance.click_edit_button("//armo-button[@buttontype='primary']//button[text()='Edit']")
        time.sleep(3)
        risk_acceptance.delete_ignore_rule()
        time.sleep(3)
