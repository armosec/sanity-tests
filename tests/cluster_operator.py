import os
import logging
import subprocess
import time, datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from .interaction_manager import InteractionManager

logger = logging.getLogger(__name__)
# FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
# logging.basicConfig(format=FORMAT)
# logger.setLevel(logging.DEBUG)

class ClusterManager:
    def __init__(self, driver, wait):
        self._driver = driver
        # self.wait = WebDriverWait(self._driver, timeout=60, poll_frequency=0.001)
        self._wait = wait
        self._interaction_manager = InteractionManager(driver)

    def login(self, email_onboarding, login_pass_onboarding, url):
        driver = self._driver
        wait = self.wait
        driver.get(url)
        wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="frontegg-login-box-container-default"]/div[1]/input')))
        mail_input = driver.find_element(by=By.XPATH, value='//*[@id="frontegg-login-box-container-default"]/div[1]/input')
        mail_input.send_keys(email_onboarding)
        mail_input.send_keys(Keys.ENTER)
        wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/frontegg-app/div[2]/div[2]/input')))
        password_input = driver.find_element(by=By.XPATH, value='/html/body/frontegg-app/div[2]/div[2]/input')
        password_input.send_keys(login_pass_onboarding)
        password_input.send_keys(Keys.ENTER)

        try:
            wait_for_element = WebDriverWait(driver, 5, 0.001)
            element = wait_for_element.until(EC.visibility_of_element_located((By.XPATH, "//div[@class='label font-semi-bold font-size-18 my-3' and contains(text(), 'What do you do?')]")))
        except:
            print("Onboarding role page is not displayed - not a sign-up user")
        else:
            print("Onboarding role page is displayed - sign-up user (first login)")
            self.handle_role_page()
        
    def handle_role_page(self):
        try:
            self._interaction_manager.click('/html/body/armo-root/div/div/div/armo-role-page/div/div[2]/div/div[1]/armo-onboarding-survey-buttons-upper/div/div[1]/div[2]', By.XPATH)
            self._interaction_manager.click('/html/body/armo-root/div/div/div/armo-role-page/div/div[2]/div/div[2]/armo-onboarding-survey-buttons-lower/div/div[1]/div[1]', By.XPATH)
            self._interaction_manager.click('/html/body/armo-root/div/div/div/armo-role-page/div/div[2]/div/div[3]/button/span[2]', By.XPATH)
            self._interaction_manager.click('/html/body/armo-root/div/div/div/armo-features-page/div/div[2]/div/div[2]/armo-onboarding-how-best-help-buttons/div[1]/div', By.XPATH)
            self._interaction_manager.click('/html/body/armo-root/div/div/div/armo-features-page/div/div[2]/div/div[3]/button/span[2]', By.XPATH)
            self._interaction_manager.click('//*[@id="mat-dialog-0"]/armo-config-scanning-connection-wizard-dialog/armo-onboarding-dialog/armo-dialog-header/header/mat-icon', By.XPATH)
            logger.info("Role page handled successfully.")
        except Exception as e:
            logger.error(f"Error handling role page: {str(e)}")
            self._driver.save_screenshot(f"./error_handling_role_page.png")

    @staticmethod
    def get_current_timestamp(format_type="default"):
        if format_type == "special":
            return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    @staticmethod
    def press_esc_key(driver):
        try:
            actions = ActionChains(driver)
            actions.send_keys(Keys.ESCAPE).perform()
            logger.info("ESC key pressed successfully.")
        except Exception as e:
            logger.error("Failed to press the ESC key.", str(e))

    def click_filter_button(self, xpath, filter_name):
        try:
            self._interaction_manager.click(xpath, By.XPATH)
            logger.info(f"{filter_name} filter clicked")
        except Exception as e:
            logger.error(f"Failed to click on {filter_name} filter button:", str(e))
            self._driver.save_screenshot(f"./failed_to_click_on_{filter_name}_filter_button_{self.get_current_timestamp()}.png")
            
    def click_close_icon_in_filter_button(self, filter_type: str):
        """
        Closes the filter of the specified type by clicking the close icon within the button.

        :param filter_type: The type of filter to close, e.g., "Severity", "Risk category".
        """
        try:
            # Find all filter buttons
            buttons = self._driver.find_elements(By.CSS_SELECTOR, "button.armo-button.secondary-neutral.md")
            
            for button in buttons:
                # Check if the button contains the filter type text
                if filter_type in button.text:
                    # Locate the armo-icon element within the button
                    close_icon = button.find_element(By.CSS_SELECTOR, "armo-icon")
                    # Locate the svg inside the armo-icon and click it
                    svg_element = close_icon.find_element(By.CSS_SELECTOR, "svg")
                    svg_element.click()
                    logger.info(f'Closed the "{filter_type}" filter.')
                    return
            
            logger.error(f'Filter with type "{filter_type}" not found.')

        except Exception as e:
            logger.error(f'Failed to close the "{filter_type}" filter: {str(e)}')
            self._driver.save_screenshot(f"./failed_to_close_{filter_type}_filter_{ClusterManager.get_current_timestamp()}.png")


    def click_on_vuln_view_button(self, button_name: str):
        try:
            button_xpath = f"//div[@class='button-toggle-label ng-star-inserted' and text()='{button_name}']/parent::a"
            button_element = self._interaction_manager.wait_until_interactable(button_xpath)
            self._driver.execute_script("arguments[0].scrollIntoView(true);", button_element)
            self._driver.execute_script("arguments[0].click();", button_element)
            logger.info(f"Clicked on '{button_name}' button successfully.")
        except Exception as e:
            logger.error(f"Failed to click on '{button_name}' button: {str(e)}")
            self._driver.save_screenshot(f"./failed_to_click_{button_name.replace(' ', '_')}_button_{self.get_current_timestamp()}.png")
            
    def click_button_by_text(self, button_text: str):
        try:
            # Find all buttons with the specific class
            buttons = self._driver.find_elements(By.CSS_SELECTOR, "button[class='armo-button tertiary sm']")
            
            for button in buttons:
                if button.text.strip() == button_text:
                    button.click()
                    logger.info(f"Clicked on button with text: '{button_text}'")
                    return
            logger.error(f"Button with text: '{button_text}' not found")
        except Exception as e:
            logger.error(f"Failed to click on button with text '{button_text}': {str(e)}")
            self._driver.save_screenshot(f"./failed_to_click_button_{button_text.replace(' ', '_')}_{ClusterManager.get_current_timestamp()}.png")
            

    def click_filter_button_in_sidebar_by_text(self, button_text: str, namespace: str = None):
        """
        Clicks a specific button within the most recently opened cdk-overlay
        based on the button's text content. If 'Attack path' namespace is provided,
        it waits for the related element before clicking.

        :param button_text: The visible text of the button to click.
        :param namespace: Optional; if provided, waits for the "Attack path" element.
        """
        try:
            # Locate all cdk-overlay-pane elements
            overlay_panes = self._driver.find_elements(By.CSS_SELECTOR, "div.cdk-overlay-pane")

            # Ensure we have found at least one cdk-overlay-pane
            if not overlay_panes:
                logger.error("No cdk-overlay-pane elements found.")
                return

            # Get the most recent overlay pane (the last one in the list)
            most_recent_overlay = overlay_panes[-1]
            
            # If the namespace is 'Attack path', wait for the specific element
            if namespace == "Attack path":
                attack_path_selector = "armo-attack-chain-graph-mini-map"
                self._wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, attack_path_selector)))
                logger.info(f"Waited for 'Attack path' specific element to appear.")

            # Otherwise, wait for the cluster and namespace element to appear
            else:
                target_selector = "div.font-size-14.font-normal.line-height-24.armo-text-black-color"
                self._wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, target_selector)))
                logger.info(f"Waited for cluster/namespace element to appear.")

            # Locate all buttons within the most recent cdk-overlay-pane
            buttons = most_recent_overlay.find_elements(By.CSS_SELECTOR, "button.armo-button.secondary-neutral.md")

            # Iterate through all buttons and click the one with the matching text
            for button in buttons:
                if button_text in button.text:
                    button.click()
                    logger.info(f"Clicked on the button with text: '{button_text}' in the most recent cdk-overlay.")
                    return

            logger.error(f"Button with text '{button_text}' not found in the most recent cdk-overlay.")

        except Exception as e:
            logger.error(f"Failed to click on the button with text '{button_text}' in the most recent cdk-overlay: {str(e)}")
            self._driver.save_screenshot(f"./failed_to_click_button_in_cdk_overlay_{ClusterManager.get_current_timestamp()}.png")


    def click_on_filter_ckackbox_filter(self, span_text: str):
        """
        Clicks a specific <span> element within the second cdk-overlay based on the span's text content.

        :param span_text: The visible text of the span to click.
        """
        try:
            # Locate all cdk-overlay-pane elements
            overlay_panes = self._driver.find_elements(By.CSS_SELECTOR, "div.cdk-overlay-pane")

            # Ensure we have at least two cdk-overlay-pane elements (since we need the second one)
            if len(overlay_panes) < 2:
                logger.error("Less than two cdk-overlay-pane elements found.")
                return

            # Get the second overlay pane (index 1)
            second_overlay = overlay_panes[1]

            # Locate all span elements within the second cdk-overlay-pane
            spans = second_overlay.find_elements(By.CSS_SELECTOR, "span.mat-tooltip-trigger.value.truncate")

            # Iterate through all spans and click the one with the matching text
            for span in spans:
                if span_text in span.text:
                    self._wait.until(EC.element_to_be_clickable(span)).click()
                    logger.info(f"Clicked on the span with text: '{span_text}' in the second cdk-overlay.")
                    return

            logger.error(f"Span with text '{span_text}' not found in the second cdk-overlay.")

        except Exception as e:
            logger.error(f"Failed to click on the span with text '{span_text}' in the second cdk-overlay: {str(e)}")
            self._driver.save_screenshot(f"./failed_to_click_span_in_second_cdk_overlay_{ClusterManager.get_current_timestamp()}.png")
            

    def verify_namespace_and_click_button(self, expected_namespace: str):
        """
        Verifies if the given namespace is present within the most recent cdk-overlay
        and clicks on the corresponding button with the 'chevron-right' icon.

        :param expected_namespace: The namespace string to verify.
        """
        try:
            # Locate all cdk-overlay-pane elements
            overlay_panes = self._driver.find_elements(By.CSS_SELECTOR, "div.cdk-overlay-pane")

            # Ensure at least one overlay pane is present
            if not overlay_panes:
                logger.error("No cdk-overlay-pane elements found.")
                return

            # Get the most recent overlay pane (the last one in the list)
            most_recent_overlay = overlay_panes[-1]

            # Locate the div elements that contain the text "Namespace:" in the most recent overlay
            elements = most_recent_overlay.find_elements(By.CSS_SELECTOR, "div.header-line")

            # Loop through the elements to find the one containing the expected namespace
            for element in elements:
                # Locate the span containing the namespace text
                namespace_span = element.find_element(By.XPATH, ".//span[contains(text(), 'Namespace:')]")
                namespace_text = namespace_span.text.strip()  # Remove any extra whitespace

                logger.info(f"Found namespace span text: '{namespace_text}'")  # Debugging output

                # Extract the actual namespace (removing "Namespace:" prefix and any whitespace)
                # We assume that 'Namespace: None' or 'Namespace: default' is the format.
                actual_namespace = namespace_text.split("Namespace:")[-1].strip()  # Extract after 'Namespace:'

                logger.info(f"Extracted actual namespace: '{actual_namespace}'")  # Debugging output

                # Check if the actual namespace matches the expected namespace
                # if actual_namespace == expected_namespace:
                #     logger.info(f"Namespace '{expected_namespace}' found in the most recent overlay.")

                    # Locate the button with the 'chevron-right' icon within the same element
                button = element.find_element(By.CSS_SELECTOR, "button.armo-button.table-secondary.sm")

                    # Scroll into view if necessary
                self._driver.execute_script("arguments[0].scrollIntoView(true);", button)

                    # Click the button
                button.click()
                logger.info(f"Clicked the button corresponding to namespace '{expected_namespace}'.")
                return

            # If the namespace was not found
            # logger.error(f"Namespace '{expected_namespace}' not found.")

        except Exception as e:
            logger.error(f"Failed to verify namespace and click the button: {str(e)}")
            self._driver.save_screenshot(f"./failed_to_verify_namespace_and_click_{expected_namespace}_{ClusterManager.get_current_timestamp()}.png")


    def get_namespace_from_element(self):
        try:
            # Locate the div element containing the namespace information
            wait = WebDriverWait(self._driver, 10)  # Wait for up to 10 seconds
            element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.font-size-14.font-normal.line-height-24.armo-text-black-color")))
            # Get the full text of the element
            full_text = element.text
            
            # Split the text to extract the part after "Namespace:"
            namespace = full_text.split("Namespace:")[1].split("|")[0].strip()
            
            logger.info(f"Extracted namespace: {namespace}")
            return namespace

        except Exception as e:
            logger.error(f"Failed to extract namespace: {str(e)}")
            self._driver.save_screenshot(f"./failed_to_extract_namespace_{ClusterManager.get_current_timestamp()}.png")
            return None

    def click_button_in_namespace_row(self, expected_namespace: str):
        """
        Clicks the second 'button.armo-button.table-secondary.sm' in the most recent cdk-overlay.
        """
        try:
            # Locate all cdk-overlay-pane elements
            overlay_panes = self._driver.find_elements(By.CSS_SELECTOR, "div.cdk-overlay-pane")

            # Ensure at least one overlay pane is present
            if not overlay_panes:
                logger.error("No cdk-overlay-pane elements found.")
                return

            # Get the most recent overlay pane (the last one in the list)
            most_recent_overlay = overlay_panes[-1]

            # Find all buttons within the most recent overlay
            buttons = most_recent_overlay.find_elements(By.CSS_SELECTOR, "button.armo-button.table-secondary.sm")

            # Ensure there are at least two buttons
            if len(buttons) < 2:
                logger.error("Less than two 'armo-button.table-secondary.sm' buttons found in the overlay.")
                return

            # Click the second button
            second_button = buttons[1]
            self._wait.until(EC.element_to_be_clickable(second_button)).click()

            logger.info(f"Clicked the second 'button.armo-button.table-secondary.sm' in the overlay.")
            print("test")
            time.sleep(3)
        except Exception as e:
            logger.error(f"Failed to click the second button in the overlay: {str(e)}")
            self._driver.save_screenshot(f"./failed_to_click_second_button_in_overlay.png")



    def run_shell_command(self, command):
        try:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            if process.returncode != 0:
                logger.error(f"Error executing command: {stderr.decode()}")
            else:
                logger.info(f"Command executed successfully: {stdout.decode()}")
        except Exception as e:
            logger.error(f"An error occurred while running the command: {str(e)}")
            
    def create_attack_path(self, manifest_filename='../manifest.yaml'):
        current_directory = os.path.dirname(os.path.realpath(__file__))
        manifest_path = os.path.join(current_directory, manifest_filename)
        command = f"kubectl apply -f {manifest_path}"
        self.run_shell_command(command)


class ConnectCluster:
    def __init__(self, driver, wait):
        self._driver = driver
        self._wait = wait
        self._interaction_manager = InteractionManager(driver)

    def click_get_started(self):
        try:
            self._interaction_manager.click('//*[@id="action-section"]/armo-button/button', By.XPATH)
            logger.info("Click on get started button.")
        except TimeoutException as e:
            logger.error("Get started button was not found or clickable.")
            self._driver.save_screenshot(f"./get_started_button_error_{ClusterManager.get_current_timestamp()}.png")

    def connect_cluster_helm(self):
        custom_wait = WebDriverWait(self._driver, timeout=180, poll_frequency=0.001)
        css_selector = 'div.command-area > span.ng-star-inserted'
        helm_command_element = custom_wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector)))
        helm_command = helm_command_element.text

        helm_command += " --set nodeAgent.config.updatePeriod=1m"
        print(f"Helm command: {helm_command}")

        try:
            result = subprocess.run(helm_command, shell=True, check=True, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            logger.error(f"Helm command execution failed with error: {e}")
            if e.stderr:
                logger.error(e.stderr.decode('utf-8'))

    def verify_installation(self):
        try:
            self._interaction_manager.click('armo-dialog-footer .mat-button-wrapper', By.CSS_SELECTOR)
        except TimeoutException as e:
            logger.error("Verify button was not found or clickable.")
            self._driver.save_screenshot(f"./verify_button_erro_{ClusterManager.get_current_timestamp()}.png")

    def view_cluster_button(self):
        try:
            self._interaction_manager.click('armo-connection-wizard-connection-step-footer .armo-button', By.CSS_SELECTOR)
            self._wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'armo-connection-wizard-connection-step-footer .armo-button')))
            time.sleep(2)
            self._interaction_manager.click('armo-connection-wizard-connection-step-footer .armo-button', By.CSS_SELECTOR)
        except TimeoutException as e:
            logger.error("View cluster button was not found or clickable.")
            self._driver.save_screenshot(f"./view_cluster_button_error_{ClusterManager.get_current_timestamp()}.png")

    def view_connected_cluster(self, custom_wait_time=10, max_attempts=2):
        try:
            # time.sleep(2)
            wait = WebDriverWait(self._driver, timeout=custom_wait_time, poll_frequency=0.001)
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'armo-cluster-scans-table .mat-tooltip-trigger')))
            logger.info("View cluster connected found.")
        except TimeoutException as e:
            if max_attempts > 0:
                logger.error(f"Failed to find view cluster connected. Refreshing page (Attempts left: {max_attempts}).")
                self._driver.save_screenshot(f"./view_connected_cluster_error_{ClusterManager.get_current_timestamp()}_attempt_{max_attempts}.png")
                self._driver.refresh()
                self.view_connected_cluster(custom_wait_time, max_attempts - 1)
            else:
                raise Exception("Element not found after maximum retry attempts.")

class Cleanup:
    def __init__(self, driver, wait):
        self._driver = driver
        self._wait = wait
        self._interaction_manager = InteractionManager(driver)

    def uninstall_kubescape(self): 
        print("Uninstalling kubescape...")
        command = "helm uninstall kubescape -n kubescape && kubectl delete ns kubescape"
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            logger.error(f"Error executing command: {stderr.decode()}")
        else:
            logger.info(f"Command executed successfully: {stdout.decode()}")

    def click_settings_button(self):
        time.sleep(1)
        self._interaction_manager.click('settings-left-menu-item', By.ID)
        logger.info("Click on settings button.")

    def click_more_options_button(self):
        time.sleep(1)
        self._interaction_manager.click('button.armo-button.table-secondary.sm', By.CSS_SELECTOR)
        logger.info("Click on more options button.")

    def choose_delete_option(self):
        time.sleep(0.5)
        self._interaction_manager.click("//button[text()='Delete']", By.XPATH)
        logger.info("Click on delete button option.")

    def confirm_delete(self):
        time.sleep(0.5)
        self._interaction_manager.click("button.mat-stroked-button[color='warn']", By.CSS_SELECTOR)
        logger.info("Click on confirm delete button.")

    def wait_for_empty_table(self):
        wait = WebDriverWait(self._driver, 180, 0.001)
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, 'td.mat-cell.text-center.ng-star-inserted'), 'No data to display'))
        logger.info("Cleanup done")

class IgnoreRule:
    def __init__(self, driver):
        self._driver = driver
        self.wait = WebDriverWait(self._driver, timeout=60, poll_frequency=0.001)
        self._interaction_manager = InteractionManager(driver)

    def click_ignore_button(self):
        try:
            self._interaction_manager.click('button.armo-button.table-secondary.sm', By.CSS_SELECTOR)
        except:
            logger.error("failed to click on 3 dots button")
            self._driver.save_screenshot(f"./ignore_button_error_{ClusterManager.get_current_timestamp()}.png")
            
        try:
            self._interaction_manager.click('.armo-button.table-secondary.lg', By.CSS_SELECTOR)
        except:
            logger.error("failed to find the Accepting the Risk button")
            self._driver.save_screenshot(f"./Accepting_Risk_button_error_{ClusterManager.get_current_timestamp()}.png")

    def get_ignore_rule_field(self, index):
        css_selector = ".mat-tooltip-trigger.field-value.truncate.ng-star-inserted"
        all_fields = self._driver.find_elements(By.CSS_SELECTOR, css_selector)
        field_text = all_fields[index].text.strip()
        logger.info(f"The RESOURCE is: '{field_text}'")
        return field_text
    
    def save_ignore_rule(self):
        try:
            self._interaction_manager.click("button.armo-button.primary.xl", By.CSS_SELECTOR)
            logger.info("Click on save ignore rule.")
        except:
            logger.error("failed to click on save button")
            self._driver.save_screenshot(f"./failed_to_click_on_save_button_{ClusterManager.get_current_timestamp()}.png")

    def igor_rule_icon_check(self):
        expected_svgsource = "/assets/icons/v2/general/edit-ignore.svg#edit-ignore"
        if expected_svgsource:
            logger.info("The icon changed to ignored.")
        else:
            logger.error("The icon does NOT change to ignored.")

    def delete_ignore_rule(self):
        try:
            self._interaction_manager.click('button.armo-button.error-secondary.xl', By.CSS_SELECTOR)
            logger.info("Click on delete ignore rule button.")
        except:
            logger.error("Not found Delete ignore rule button.")
            self._driver.save_screenshot(f"./delete_ignore_rule_button_error_{ClusterManager.get_current_timestamp()}.png")

        try:
            self._interaction_manager.click('.mat-focus-indicator.base-button.big-button.mat-stroked-button.mat-button-base.mat-warn', By.CSS_SELECTOR)
            logger.info("Ignore rule deleted.")
        except:
            logger.error("Revoke button not found.")
            self._driver.save_screenshot(f"./revoke_button_error_{ClusterManager.get_current_timestamp()}.png")



class RiskAcceptancePage:
    def __init__(self, driver):
        self._driver = driver
        self.wait = WebDriverWait(self._driver, timeout=60, poll_frequency=0.001)
        self._interaction_manager = InteractionManager(driver)

    def navigate_to_page(self):
        try:
            self._interaction_manager.click("rick-acceptance-left-menu-item", By.ID)
            logger.info("Clicked on Risk Acceptance page.")
        except Exception as e:
            logger.error(f"Error clicking on Risk Acceptance page: {e}")
            self._driver.save_screenshot(f"./failed_to_click_on_risk_acceptance_page_{ClusterManager.get_current_timestamp()}.png")

    def click_severity_element(self, css_selector):
        try:
            self._interaction_manager.click(css_selector, By.CSS_SELECTOR)
            logger.info("Clicked on the severity element.")
        except Exception:
            logger.error(f"Failed to click on the severity element: {css_selector}")
            self._driver.save_screenshot(f"./failed_to_click_severity_element_{ClusterManager.get_current_timestamp()}.png")

    def click_edit_button(self, xpath):
        try:
            self._interaction_manager.click(xpath, By.XPATH)
            logger.info("Clicked the Edit button.")
        except Exception as e:
            logger.error(f"Error clicking the Edit button: {e}")
            self._driver.save_screenshot(f"./failed_to_click_edit_button_{ClusterManager.get_current_timestamp()}.png")

    def delete_ignore_rule(self):
        try:
            ignore_rule = IgnoreRule(self._driver)
            ignore_rule.delete_ignore_rule()
            time.sleep(4)
        except Exception as e:
            logger.error(f"Failed to delete ignore rule: {e}")
            self._driver.save_screenshot(f"./failed_to_delete_ignore_rule_{ClusterManager.get_current_timestamp()}.png")

    def switch_tab(self, tab_name):
        try:
            tab_hrefs = {
                "Security Risks": "/risk-acceptance?tab=security-risks",
                "Vulnerabilities": "/risk-acceptance?tab=vulnerabilities",
                "Compliance": "/risk-acceptance?tab=compliance"
            }

            tab_href = tab_hrefs.get(tab_name)
            if not tab_href:
                logger.error(f"Tab '{tab_name}' not found.")
                return

            tab_xpath = f"//a[@href='{tab_href}']"
            self._interaction_manager.click(tab_xpath, By.XPATH)
            logger.info(f"Switched to '{tab_name}' tab successfully.")
        except Exception as e:
            logger.error(f"Failed to switch to '{tab_name}' tab: {str(e)}")
            self._driver.save_screenshot(f"./failed_to_switch_to_{tab_name.replace(' ', '_')}_tab_{ClusterManager.get_current_timestamp()}.png")
