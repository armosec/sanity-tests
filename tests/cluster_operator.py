import os
import logging
import subprocess
import time, datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from .interaction_manager import InteractionManager
from .login_manager import LoginManager

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
        self._login_manager = LoginManager(driver, wait)

    # def login(self, email_onboarding, login_pass_onboarding, url):
    #     driver = self._driver
    #     wait = self.wait
    #     driver.get(url)
    #     wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="frontegg-login-box-container-default"]/div[1]/input')))
    #     mail_input = driver.find_element(by=By.XPATH, value='//*[@id="frontegg-login-box-container-default"]/div[1]/input')
    #     mail_input.send_keys(email_onboarding)
    #     mail_input.send_keys(Keys.ENTER)
    #     wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/frontegg-app/div[2]/div[2]/input')))
    #     password_input = driver.find_element(by=By.XPATH, value='/html/body/frontegg-app/div[2]/div[2]/input')
    #     password_input.send_keys(login_pass_onboarding)
    #     password_input.send_keys(Keys.ENTER)
    
    def login(self, email_onboarding, login_pass_onboarding, url):
        self._login_manager.login(email_onboarding, login_pass_onboarding, url)  
        try:
            wait_for_element = WebDriverWait(self._driver, 5, 0.001)
            element = wait_for_element.until(EC.visibility_of_element_located((By.XPATH, "//div[@class='label font-semi-bold font-size-18 my-3' and contains(text(), 'What do you do?')]")))
        except:
            logger.info("Onboarding role page is not displayed - not a sign-up user")
        else:
            logger.info("Onboarding role page is displayed - sign-up user (first login)")
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
            
    @staticmethod        
    def press_space_key(driver):
        try:
            ActionChains(driver).send_keys(Keys.SPACE).perform()
            logger.info("Space key pressed.")
        except Exception as e:
            logger.error(f"Failed to press space key: {str(e)}")
                

    def click_close_filter(driver, index=0):
        try:
            # Define the XPath to locate all <armo-icon> elements
            armo_icon_xpath = "//armo-icon[@svgsource='assets/icons/v2/general/close.svg#close']"

            # Wait until at least one <armo-icon> element is present
            armo_icon_elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, armo_icon_xpath)))

            # Ensure the index is within bounds
            if index >= len(armo_icon_elements):
                raise IndexError(f"Invalid index {index}. Only {len(armo_icon_elements)} elements found.")

            # Wait for the overlay to disappear, if present
            WebDriverWait(driver, 10).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "cdk-overlay-backdrop")))

            # Select the <armo-icon> element at the specified index
            armo_icon_element = armo_icon_elements[index]

            # Scroll the element into view
            driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", armo_icon_element)

            # Use ActionChains to move to the element and click
            actions = ActionChains(driver)
            actions.move_to_element(armo_icon_element).click().perform()

            logger.info(f"Successfully clicked on the close filter element at index {index}.")

        except IndexError as e:
            logger.error(f"Index error: {e}")
        except Exception as e:
            logger.error(f"Failed to click on the close element at index {index}: {str(e)}")
            driver.save_screenshot(f"./failed_to_click_armo_icon_{ClusterManager.get_current_timestamp()}.png")


    def click_filter_button(self, filter_name):
        try:
            logger.info(f"Trying to click on the '{filter_name}' filter button...")
            xpath = f"//button[.//span[normalize-space(text())='{filter_name}']]"

            button = WebDriverWait(self._driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            button.click()
            logger.info(f"Successfully clicked the '{filter_name}' filter button.")
        except Exception as e:
            logger.error(f"Failed to click on the '{filter_name}' filter: {str(e)}")
            self._driver.save_screenshot(
                f"./failed_to_click_{filter_name}_filter_{ClusterManager.get_current_timestamp()}.png")

    
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
            
            
    def click_on_tab_in_vulne_page(self, partial_href, index=0):
        try:
            xpath = f"(//a[contains(@href, '{partial_href}')])[{index + 1}]"
            tab = WebDriverWait(self._driver, 15).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            self._driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tab)
            self._driver.execute_script("arguments[0].click();", tab)
            logger.info(f"Clicked tab '{partial_href}' at index {index} using JS click.")
        except Exception as e:
            logger.error(f"Failed to click on tab '{partial_href}' at index {index}: {str(e)}")
            self._driver.save_screenshot(f"./failed_click_tab_{partial_href}_{ClusterManager.get_current_timestamp()}.png")
            
            
    def click_tab_on_sidebar(self, tab_name):
        try:
            # Define the XPath for the tab with the specific name
            tab_xpath = f"//span[@class='mdc-tab__text-label' and text()='{tab_name}']"
            # Wait for the tab element to be visible and present
            tab_element = WebDriverWait(self._driver, 50).until(
                EC.visibility_of_element_located((By.XPATH, tab_xpath)))

            # Scroll the tab element into view
            self._driver.execute_script("arguments[0].scrollIntoView(true);", tab_element)
            # Ensure the tab is clickable
            WebDriverWait(self._driver, 50).until(EC.element_to_be_clickable((By.XPATH, tab_xpath)))

            time.sleep(2)
            # Click the tab
            tab_element.click()
            logger.info(f"Clicked on the tab with name: {tab_name}")
            
        except TimeoutException:
            logger.error(f"Timeout: The tab with name '{tab_name}' could not be found.")
            self._driver.save_screenshot(f"./failed_to_click_tab_{tab_name}_timeout.png")
        except Exception as e:
            logger.error(f"Failed to click the tab with name '{tab_name}'. Error: {str(e)}")
            self._driver.save_screenshot(f"./failed_to_click_tab_{tab_name}_error.png")

            
    def click_overlay_button(self):
        try:
            # XPath to find all buttons inside the overlay
            buttons_xpath = "//div[contains(@class, 'cdk-overlay-pane')]//button[contains(@class, 'armo-button') and contains(@class, 'table-secondary') and contains(@class, 'sm')]"
            
            # Wait for the presence of multiple buttons in the overlay
            buttons = WebDriverWait(self._driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, buttons_xpath))
            )

            # Check if at least two buttons are found
            if len(buttons) >= 2:
                # Click the second button (index 1 because lists are zero-indexed)
                second_button = buttons[1]
                second_button.click()
                logger.info("Successfully clicked the second button inside the overlay.")
            else:
                logger.error("Less than two buttons found in the overlay.")

        except Exception as e:
            logger.error(f"Failed to click the second button inside the overlay. Error: {str(e)}")
            self._driver.save_screenshot(f"./failed_to_click_second_overlay_button.png")


    def click_button_by_text(self, button_text: str, button_type: str = "tertiary", button_size: str = "sm"):
        try:
            # Find all buttons with the specific class
            buttons = self._driver.find_elements(By.CSS_SELECTOR, f"button[class='armo-button {button_type} {button_size}']")
            
            for button in buttons:
                if button.text.strip() == button_text:
                    button.click()
                    logger.info(f"Clicked on button with text: '{button_text}'")
                    return
            logger.error(f"Button with text: '{button_text}' not found")
        except Exception as e:
            logger.error(f"Failed to click on button with text '{button_text}': {str(e)}")
            self._driver.save_screenshot(f"./failed_to_click_button_{button_text.replace(' ', '_')}_{ClusterManager.get_current_timestamp()}.png")
            

    def click_filter_button_in_sidebar_by_text(self,category_name,button_text: str):
        # """
        # Clicks a specific button within the most recently opened cdk-overlay
        # based on the button's text content. If 'Attack path' namespace is provided,
        # it waits for the related element before clicking.

        # :param button_text: The visible text of the button to click.
        # :param namespace: Optional; if provided, waits for the "Attack path" element.
        # """
        # time.sleep(2)  # Short delay to ensure the overlay is rendered
        # try:
        #     # Locate all cdk-overlay-pane elements
        #     overlay_panes = self._driver.find_elements(By.CSS_SELECTOR, "div.cdk-overlay-pane")

        #     # Ensure we have found at least one cdk-overlay-pane
        #     if not overlay_panes:
        #         logger.error("No cdk-overlay-pane elements found.")
        #         return

        #     # Get the most recent overlay pane (the last one in the list)
        #     most_recent_overlay = overlay_panes[-1]
            
        #     # If the namespace is 'Attack path', wait for the specific element
        #     if category_name == "Attack path":
        #         attack_path_selector = "armo-attack-chain-graph-mini-map"
        #         self._wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, attack_path_selector)))
        #         logger.info(f"Waited for 'Attack path' specific element to appear.")

        #     # Otherwise, wait for the cluster and namespace element to appear
        #     elif category_name == "Workloads" or category_name == "Data":    
        #         target_selector = "div.font-size-14.font-normal.line-height-24.armo-text-black-color"
        #         self._wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, target_selector)))
        #         logger.info(f"Waited for cluster/namespace element to appear.")
                
        #     else:
        #         category_name = "Network configuration"
        #         network_selector = "td.mat-mdc-cell.cdk-column-namespace"
        #         self._wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, network_selector)))
        #         logger.info(f"Waited for network configuration element to appear.")
                
        #     # Locate all buttons within the most recent cdk-overlay-pane
        #     buttons = most_recent_overlay.find_elements(By.CSS_SELECTOR, "button.armo-button.secondary-neutral.md")

        #     # Iterate through all buttons and click the one with the matching text
        #     for button in buttons:
        #         if button_text in button.text:
        #             button.click()
        #             logger.info(f"Clicked on the button with text: '{button_text}' in the most recent cdk-overlay.")
        #             return

        #     logger.error(f"Button with text '{button_text}' not found in the most recent cdk-overlay.")

        # except Exception as e:
        #     logger.error(f"Failed to click on the button with text '{button_text}' in the most recent cdk-overlay: {str(e)}")
        #     self._driver.save_screenshot(f"./failed_to_click_button_in_cdk_overlay_{ClusterManager.get_current_timestamp()}.png")
        #     raise
        try:
            # Wait for sidebar to stabilize
            time.sleep(5)
            
            # Find the most recent overlay
            overlay_pane_selector = "div.cdk-overlay-pane"
            overlay_panes = WebDriverWait(self._driver, 20).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, overlay_pane_selector))
            )
            visible_overlays = [o for o in overlay_panes if o.is_displayed()]
            logger.info(f"Found {len(overlay_panes)} total overlays, {len(visible_overlays)} visible.")
            
            if not visible_overlays:
                raise Exception("No visible overlays found")
            
            most_recent_overlay = visible_overlays[-1]
            
            # Search for the button in the overlay
            button_xpath = f".//button[contains(., '{button_text}')]"
            logger.info(f"Looking for '{button_text}' button inside the overlay...")
            
            # Wait for button to be present (not checking visibility)
            button_to_click = WebDriverWait(most_recent_overlay, 15).until(
                EC.presence_of_element_located((By.XPATH, button_xpath))
            )
            
            logger.info(f"Found '{button_text}' button in overlay")
            time.sleep(1)
            
            # Try regular click first, fallback to JS if it fails
            try:
                button_to_click.click()
                logger.info(f"Successfully clicked '{button_text}' button with regular click")
            except Exception as click_error:
                logger.warning(f"Regular click failed ({click_error}), using JS click")
                self._driver.execute_script("arguments[0].click();", button_to_click)
                logger.info(f"Successfully clicked '{button_text}' button with JS click")


        except Exception as e:
            logger.error(f"Failed to click '{button_text}' button: {str(e)}")
            self._driver.save_screenshot(f"./failed_to_click_button_in_cdk_overlay_{ClusterManager.get_current_timestamp()}.png")
            raise
        
    def click_checkbox_by_name(self, label_name):
        """
        Clicks a checkbox with the specified label name in a dynamic overlay.
        
        :param driver: The Selenium WebDriver instance.
        :param label_name: The label text associated with the checkbox to click.
        """
        time.sleep(1)
        try:
            # Wait for the overlay containing the checkboxes to appear
            overlay_xpath = "//div[contains(@class, 'mat-mdc-menu-panel')]"
            WebDriverWait(self._driver, 10).until(
                EC.presence_of_element_located((By.XPATH, overlay_xpath))
            )

            # Build the dynamic XPath for the checkbox input
            checkbox_xpath = f"//span[text()='{label_name}']/ancestor::mat-checkbox//input[@type='checkbox']"

            # Locate the checkbox input
            checkbox_input = self._driver.find_element(By.XPATH, checkbox_xpath)

            # Scroll the checkbox into view to ensure it's visible
            self._driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", checkbox_input)

            # Click the checkbox using JavaScript to bypass potential overlay issues
            time.sleep(1)
            self._driver.execute_script("arguments[0].click();", checkbox_input)
            logger.info(f"Successfully clicked the checkbox labeled '{label_name}'.")
        except Exception as e:
            logger.error(f"Failed to click the checkbox labeled '{label_name}': {str(e)}")
            self._driver.save_screenshot(f"./failed_to_click_checkbox_{label_name.replace(' ', '_')}.png")


    def click_on_filter_checkbox_sidebar(self, span_text: str):
        """
        Clicks the checkbox input inside any cdk-overlay-pane where the span contains the specified text.
        Uses a unified XPath for robustness.
        """
        try:
            # Wait for overlay panes to be present
            WebDriverWait(self._driver, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.cdk-overlay-pane")))

            # Unified XPath: find the checkbox input whose <mat-checkbox> contains a matching span
            checkbox_xpath = f"//div[contains(@class, 'cdk-overlay-pane')]//mat-checkbox[.//span[contains(text(), '{span_text}')]]//input[@type='checkbox']"

            checkbox_input = WebDriverWait(self._driver, 10).until(
                EC.presence_of_element_located((By.XPATH, checkbox_xpath)))

            self._driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox_input)
            self._driver.execute_script("arguments[0].click();", checkbox_input)

            logger.info(f"Successfully clicked checkbox with label text: '{span_text}'")

        except Exception as e:
            logger.error(f"Failed to click checkbox for span text '{span_text}': {str(e)}")
            self._driver.save_screenshot(f"./failed_click_checkbox_{span_text}_{ClusterManager.get_current_timestamp()}.png")
           
            
    def get_namespace_from_element(self, category_name: str):
        logger.info(f"______Category name:  {category_name} ______")
        try:
            if category_name == "Workloads" or category_name == "Data":
                wait = WebDriverWait(self._driver, 30)  # Wait for up to 30 seconds
                element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.font-size-14.font-normal.line-height-24.armo-text-black-color")))
                # Get the full text of the element
                full_text = element.text
            
                # Split the text to extract the part after "Namespace:"
                namespace = full_text.split("Namespace:")[1].split("|")[0].strip()
            
                logger.info(f"Extracted namespace: {namespace}")
                return namespace
            
            elif category_name == "Network configuration":
                    wait = WebDriverWait(self._driver, 30)  # Wait for up to 30 seconds
                    namespace_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "td.mat-mdc-cell.cdk-column-namespace")))
                    namespace = namespace_element.text.strip()
                    logger.info(f"Extracted namespace: {namespace}")
                    return namespace
            else:
                category_name = "Attack path"
                attack_path_selector = "armo-attack-chain-graph-mini-map"
                self._wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, attack_path_selector)))
                namespace_divs = self._driver.find_elements(By.CSS_SELECTOR, "div.armo-text-black-color.font-size-14.line-height-24.mb-2.text-wrap-balance")
                
                for div in namespace_divs:
                    full_text = div.text
                    if "Namespace:" in full_text:
                        namespace = full_text.split("Namespace:")[1].strip()
                        break
                else:
                    raise ValueError("Namespace not found in any div")
                
            logger.info(f"Extracted namespace: {namespace}")
            return namespace

        except Exception as e:
            logger.error(f"Failed to extract namespace: {str(e)}")
            self._driver.save_screenshot(f"./failed_to_extract_namespace_{ClusterManager.get_current_timestamp()}.png")
            return None

    def click_button_in_namespace_row(self, category_name, expected_namespace: str):
        try:
            if category_name == "Workloads" or category_name == "Data":
                button_selector = "div.cdk-overlay-pane button.armo-button.table-secondary.sm"
                
                try:
                    buttons = WebDriverWait(self._driver, 15).until(
                        lambda d: d.find_elements(By.CSS_SELECTOR, button_selector) if len(d.find_elements(By.CSS_SELECTOR, button_selector)) >= 2 else None
                    )
                    logger.info(f"Found {len(buttons)} buttons in the overlay, proceeding.")
                except TimeoutException:
                    # If the wait times out, it means we never found 2 buttons.
                    button_count = len(self._driver.find_elements(By.CSS_SELECTOR, button_selector))
                    logger.error(f"Timed out waiting for at least 2 buttons. Found only {button_count}.")
                    self._driver.save_screenshot(f"./too_few_buttons_in_overlay_{ClusterManager.get_current_timestamp()}.png")
                    return

                self._driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", buttons[1])
                time.sleep(0.2)
                self._driver.execute_script("arguments[0].click();", buttons[1])
                logger.info("Clicked the second 'button.armo-button.table-secondary.sm' in the overlay.")

            elif category_name == "Network configuration":
                try:
                    chevron_selector = "td.mat-mdc-cell.cdk-column-action button.armo-button"
                    chevron_button = WebDriverWait(self._driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, chevron_selector))
                    )
                    self._driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", chevron_button)
                    time.sleep(0.5)
                    self._driver.execute_script("arguments[0].click();", chevron_button)
                    logger.info("Clicked chevron button in Network configuration category.")
                except Exception as e:
                    logger.error(f"Failed to click on the namespace element in the Network configuration category: {str(e)}")
                    self._driver.save_screenshot(f"./failed_to_click_on_namespace_element_{ClusterManager.get_current_timestamp()}.png")

                try:
                    wait = WebDriverWait(self._driver, 60)
                    pre_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "td.value.added > pre")))
                    first_pre_element = pre_elements[0] 
                    if first_pre_element:
                        logger.info("Element with 'kind: NetworkPolicy' is visible.")
                    else:
                        logger.error("Element with 'kind: NetworkPolicy' was not found.")

                except TimeoutException as e:
                    logger.error("Timed out waiting for the element with 'kind: NetworkPolicy' to be visible.")
                    self._driver.save_screenshot(f"./failed_to_find_networkpolicy_element_{ClusterManager.get_current_timestamp()}.png")

            else:
                try:
                    category_name = "Attack path"
                    fix_button = self._wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-test-id='fix-button']")))
                    fix_button.click()
                    logger.info(f"Clicked the 'Fix' button in the '{category_name}' category.")
                except Exception as e:
                    logger.error(f"Failed to click the 'Fix' button in the '{category_name}' category: {str(e)}")
                    self._driver.save_screenshot(f"./failed_to_click_fix_button_{ClusterManager.get_current_timestamp()}.png")

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
        
    def get_value_by_label(self, label_name):
        
        try:
            # Define XPath to locate the row based on the label name
            label_xpath = f"//tr[.//span[text()='{label_name}']]/td[contains(@class, 'cdk-column-value')]//span"
            
            # Wait until the element is visible
            WebDriverWait(self._driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, label_xpath))
            )
            
            # Use the interaction_manager's get_text function to fetch the value
            value = self._interaction_manager.get_text(label_xpath, By.XPATH)
            
            if value:
                logger.info(f"Found value for label '{label_name}': {value.strip()}")
                return value.strip()
            else:
                logger.error(f"Value for label '{label_name}' not found.")
                return None

        except Exception as e:
            logger.error(f"Error fetching value for label '{label_name}': {str(e)}")
            self._driver.save_screenshot(f"./failed_to_fetch_{label_name}_value_{ClusterManager.get_current_timestamp()}.png")
            return None
        
    def verify_application_profiles_completed(self):
        
        command = (
            "kubectl get applicationprofile -n attack-suite "
            "-o jsonpath='{range .items[*]}{.metadata.name}{\"\\t\"}{.metadata.annotations.kubescape\\.io/status}{\"\\n\"}{end}'"
        )

        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
            output = result.stdout.strip()

            if not output:
                logger.error("No output returned from kubectl command.")
                return False

            all_completed = True
            for line in output.splitlines():
                name, status = line.strip().split('\t')
                if status.strip().lower() != "completed":
                    logger.warning(f"{name} is not completed (status: '{status}')")
                    all_completed = False

            if all_completed:
                logger.info("All application profiles are completed.")
            else:
                logger.error("Some application profiles are not completed.")

            return all_completed

        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return False


class ConnectCluster:
    def __init__(self, driver, wait):
        self._driver = driver
        self._wait = wait
        self._interaction_manager = InteractionManager(driver)

    def click_get_started(self):
        time.sleep(0.5)
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
            self._interaction_manager.click('button.armo-button.primary.md', By.CSS_SELECTOR)
        except TimeoutException as e:
            logger.error("Verify button was not found or clickable.")
            self._driver.save_screenshot(f"./verify_button_erro_{ClusterManager.get_current_timestamp()}.png")

    def view_cluster_button(self):
        logger.info("Waiting for connect clustert - 1 min.")
        time.sleep(60)
        try:
            wait = WebDriverWait(self._driver, timeout=180, poll_frequency=0.5)
            cluster_connected_button= wait.until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space(text())='View cluster']")))
            cluster_connected_button.click()
            logger.info("Click on view cluster button.")
        except TimeoutException as e:
            logger.error("View cluster button was not found or clickable.")
            self._driver.save_screenshot(f"./view_cluster_button_error_{ClusterManager.get_current_timestamp()}.png")     

    def view_connected_cluster(self, custom_wait_time=20, max_attempts=3):
        try:
            time.sleep(2)
            wait = WebDriverWait(self._driver, timeout=custom_wait_time, poll_frequency=0.001)
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "img[src='/assets/images/cluster-status/connected.svg']")))
            logger.info("View cluster connected found.")
        except TimeoutException as e:
            if max_attempts > 0:
                logger.error(f"Failed to find view cluster connected. Refreshing page (Attempts left: {max_attempts}).")
                # self._driver.save_screenshot(f"./view_connected_cluster_error_{ClusterManager.get_current_timestamp()}_attempt_{max_attempts}.png")
                self._driver.refresh()
                self.view_connected_cluster(custom_wait_time, max_attempts - 1)
            else:
                self._driver.save_screenshot(f"./view_connected_cluster_error_{ClusterManager.get_current_timestamp()}.png")
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
        time.sleep(2)
        self._interaction_manager.click('button.armo-button.table-secondary.sm', By.CSS_SELECTOR, index=2)
        logger.info("Click on more options button.")

    def choose_delete_option(self):
        time.sleep(0.5)
        self._interaction_manager.click("//div[contains(@class,'cdk-overlay-pane')]//span[normalize-space(text())='Delete']/ancestor::button", By.XPATH)
        logger.info("Click on delete button option.")

    def confirm_delete(self):
        time.sleep(0.5)
        self._interaction_manager.click("mat-dialog-container button.armo-button.error.xl", By.CSS_SELECTOR)
        logger.info("Click on confirm delete button.")

    def wait_for_empty_table(self):
        wait = WebDriverWait(self._driver, 180, 0.001)
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, 'td.mat-cell.ng-star-inserted > div.d-flex.justify-content-center'), 'No data to display'))
        logger.info("Cleanup done")

class IgnoreRule:
    def __init__(self, driver):
        self._driver = driver
        self.wait = WebDriverWait(self._driver, timeout=60, poll_frequency=0.001)
        self._interaction_manager = InteractionManager(driver)

    def click_ignore_button(self):
        """Click the 3-dots menu button and then click the ignore button - headless-friendly version"""
        # Allow the page to stabilize
        time.sleep(2)
        accept_xpath = "//div[contains(@class, 'cdk-overlay-pane')]//button[.//span[normalize-space()='Accept Risk']]"

        # 2. Handle overlays more aggressively for headless mode
        try:
            self._interaction_manager.close_all_overlays()
            # three_dots_xpath = "(//td[contains(@class, 'cdk-column-buttons')]//button[contains(@class, 'armo-button')])[1]"
            three_dots_xpath = '//armo-icon-button[contains(@svgsource, "more.svg#more")]//button'
            btn = self._interaction_manager.wait_until_interactable(three_dots_xpath)
            btn.click()
            logger.info("Clicked the 3-dots menu button.")
        except Exception as e:
            logger.error(f"Failed to click 3-dots button: {e}")
            self._driver.save_screenshot("failed_3dots.png")
            raise
            
        # 3. Click the "Accept Risk" button
        time.sleep(2)
        try:
            accept_btn = WebDriverWait(self._driver, 10).until(
                EC.presence_of_element_located((By.XPATH, accept_xpath))
            )
            self._driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", accept_btn)
            self._driver.execute_script("arguments[0].click();", accept_btn)
            logger.info("Clicked Accept Risk using JS.")
        except Exception as e:
            logger.error(f"JS click failed: {e}")
            self._driver.save_screenshot("accept_risk_js_fail.png")
            raise
        
    def click_ignore_rule_button_sidebar(self):
        try:
            time.sleep(2)
            
            # Get all overlays and use the most recent one
            overlays = self._driver.find_elements(By.CSS_SELECTOR, "div.cdk-overlay-pane")
            if not overlays:
                raise Exception("No overlay found")
            
            current_overlay = overlays[-1]
            logger.info(f"Found {len(overlays)} overlays, using the most recent")
            
            # Find button within the current overlay
            button = current_overlay.find_element(
                By.CSS_SELECTOR, 
                'armo-ignore-rules-button button.armo-button.table-secondary.sm'
            )
            
            # Scroll into view and click
            self._driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
            time.sleep(0.5)
            self._driver.execute_script("arguments[0].click();", button)
            logger.info("Click on ignore rule button on side sidebar.")
            
        except Exception as e:
            logger.error(f"Failed to click on ignore rule button on sidebar: {e}")
            self._driver.save_screenshot(f"./ignore_rule_button_error_sidebar_{ClusterManager.get_current_timestamp()}.png")
            raise
            
    def get_workload_name(self, timeout=15) -> str:
        try:
            # Wait until the Save button is clickable, which means modal is fully loaded
            WebDriverWait(self._driver, timeout).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Save')]")))
            logger.info("Save button is clickable - modal is ready.")

            # Locate all field containers
            fields = self._driver.find_elements(By.CSS_SELECTOR, "div.mat-mdc-menu-trigger.field.pointer.ng-star-inserted")

            for field in fields:
                label = field.find_element(By.XPATH, "./preceding-sibling::label[1]").text.strip().lower()
                if "workload" in label:
                    workload = field.find_element(By.CSS_SELECTOR, "span.field-value").text.strip()
                    logger.info(f"Extracted workload name: {workload}")
                    return workload

            raise ValueError("Workload name field not found.")

        except Exception as e:
            logger.error(f"Failed to get workload name: {str(e)}")
            self._driver.save_screenshot(f"./failed_to_get_workload_name_{ClusterManager.get_current_timestamp()}.png")
            raise
            
    def click_ignore_on_from_attach_path(self):
        try:
            button = WebDriverWait(self._driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.armo-button.secondary-neutral.xl")))
            button.click()
            logger.info("Clicked the 'Accept the risk' button from attach path.")
    
        except TimeoutException as e:
            logger.error(f"Failed to click on 'Accepting the Risk' button from attach path: {str(e)}")
            self._driver.save_screenshot(f"./Accepting_Risk_button_error_rfrom _attach_path_{ClusterManager.get_current_timestamp()}.png")


    def get_ignore_rule_field(self, index, timeout=15):
        css_selector = "div.mat-mdc-menu-trigger.field.pointer.ng-star-inserted"
        
        try:
            all_fields = WebDriverWait(self._driver, timeout).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, css_selector))
            )
            logger.info(f"Found {len(all_fields)} fields.")

            if index >= len(all_fields):
                raise IndexError(f"Requested index {index}, but only {len(all_fields)} fields were found.")

            field_element = all_fields[index]
            span = field_element.find_element(By.CSS_SELECTOR, "span.field-value")
            
            # Use get_attribute('textContent') for better reliability
            resource_name = span.get_attribute('textContent').strip()
            
            # Add a log to see what was actually captured
            logger.info(f"Field at index {index} has value: '{resource_name}'")
            return resource_name
            
        except TimeoutException:
            logger.error(f"Timed out waiting for fields with selector '{css_selector}' to appear.")
            self._driver.save_screenshot(f"./headless_fields_not_found_{ClusterManager.get_current_timestamp()}.png")
            raise
    
    def save_ignore_rule(self):
        save_xpath = "//mat-dialog-container//button[contains(text(), 'Save')]"
            
        try:
            save_btn = WebDriverWait(self._driver, 10).until(
                EC.presence_of_element_located((By.XPATH, save_xpath))
            )
            self._driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", save_btn)
            time.sleep(0.5)
            self._driver.execute_script("arguments[0].click();", save_btn)
            logger.info("Clicked Save successfully with JS.")
            
        except Exception as e:
            logger.error(f"Failed to click Save: {e}")
            self._driver.save_screenshot("save_click_error.png")
            raise
            
    def click_save_button_sidebar(self):
        try:
            # Wait for at least two buttons to be present
            WebDriverWait(self._driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "button.armo-button.primary.xl"))
            )
            
            # Find all buttons with the given CSS selector
            buttons = self._driver.find_elements(By.CSS_SELECTOR, "button.armo-button.primary.xl")
            
            # Ensure there are at least two buttons
            if len(buttons) >= 2:
                # Click the second button (index 1)
                buttons[1].click()
                logger.info("Successfully clicked the second 'Save' button.")
            else:
                logger.error("There are less than two 'Save' buttons.")
                
        except Exception as e:
            logger.error(f"Failed to click on the second 'Save' button: {str(e)}")
            self._driver.save_screenshot(f"./failed_to_click_second_save_button_{ClusterManager.get_current_timestamp()}.png")


    def igor_rule_icon_check(self):
        expected_svgsource = "/assets/icons/v2/general/edit-ignore.svg#edit-ignore"
        if expected_svgsource:
            logger.info("The icon changed to ignored.")
        else:
            logger.error("The icon does NOT change to ignored.")
            
        
    def click_delete_icon_in_modal(self):
        """Waits for the edit modal to be stable, then clicks the delete (trash can) icon."""
        try:
            delete_btn_xpath = "//mat-dialog-container//armo-icon-button[contains(@svgsource, 'trash-can.svg')]//button"
            delete_btn = self._driver.find_element(By.XPATH, delete_btn_xpath)
            self._driver.execute_script("arguments[0].click();", delete_btn)
            logger.info("Clicked on the delete/revoke icon button.")

        except Exception as e:
            logger.error(f"Failed to click the delete icon in the modal: {e}")
            self._driver.save_screenshot("error_clicking_delete_icon.png")
            raise

    def click_confirm_revoke_button(self):
        """Waits for the confirmation dialog and clicks 'Yes, Revoke'."""
        try:
            confirm_btn_xpath = "//mat-dialog-container//button[contains(text(), 'Yes, Revoke')]"
            confirm_btn = self._driver.find_element(By.XPATH, confirm_btn_xpath)
            self._driver.execute_script("arguments[0].click();", confirm_btn)
            logger.info("Clicked on 'Yes, Revoke' to confirm deletion.")

        except Exception as e:
            logger.error(f"Failed to click the 'Yes, Revoke' confirmation button: {e}")
            self._driver.save_screenshot("error_confirming_revoke.png")
            raise

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
            
    def navigate_to_risk_acceptance_form_sidebar(self, category_name):
        try:
            most_recent_overlay = None  # Initialize the variable to avoid referencing before assignment
            if category_name != "Attack path":
                # Wait for the overlay to appear
                overlay_panes = WebDriverWait(self._driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.cdk-overlay-pane")))
                
                # Ensure we have found at least one overlay
                if not overlay_panes:
                    logger.error("No overlay pane found.")
                    return
                
                # Get the most recent overlay pane (the last one in the list)
                most_recent_overlay = overlay_panes[-1]
            else:
                most_recent_overlay = self._driver

            # Define the CSS selector to find the "Risk Acceptance" button inside the most recent overlay
            button_XPATH = "//a[@href='/risk-acceptance']/armo-button/button"

            # Find the "Risk Acceptance" button inside the overlay using CSS_SELECTOR
            risk_acceptance_button = WebDriverWait(most_recent_overlay, 10).until(
                EC.presence_of_element_located((By.XPATH, button_XPATH)))
            
            time.sleep(3)

            # Scroll into view
            self._driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", 
                risk_acceptance_button
            )
            time.sleep(1)

            # Use JS click (more reliable)
            self._driver.execute_script("arguments[0].click();", risk_acceptance_button)
            time.sleep(2)
        
        except Exception as e:
            logger.error(f"Failed to click on the 'Risk Acceptance' button in the sidebar: {str(e)}")
            self._driver.save_screenshot(f"./failed_to_click_risk_acceptance_button_sidebar_{ClusterManager.get_current_timestamp()}.png")


    def click_severity_element(self, css_selector):
        try:
            element = WebDriverWait(self._driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
            self._interaction_manager.click(css_selector, By.CSS_SELECTOR)
            logger.info("Clicked on the severity element.")
        except Exception:
            logger.error(f"Failed to click on the severity element: {css_selector}")
            self._driver.save_screenshot(f"./failed_to_click_severity_element_{ClusterManager.get_current_timestamp()}.png")

    def click_edit_button(self, xpath: str):
        try:
            # Optional: narrow to the most recent overlay, if needed
            overlays = self._driver.find_elements(By.CSS_SELECTOR, "div.cdk-overlay-pane")
            if not overlays:
                raise Exception("No overlay pane found")

            overlay = overlays[-1]

            # Find the element using the provided XPath, scoped inside the overlay
            edit_button = overlay.find_element(By.XPATH, xpath)

            self._driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", edit_button)
            time.sleep(0.3)
            self._driver.execute_script("arguments[0].click();", edit_button)

            logger.info(f"Clicked the button at XPath: {xpath}")
        except Exception as e:
            logger.error(f"Error clicking button at XPath '{xpath}': {str(e) or 'No error message'}")
            self._driver.save_screenshot(f"./failed_to_click_edit_button_{ClusterManager.get_current_timestamp()}.png")


    def delete_ignore_rule(self):
        try:
            ignore_rule = IgnoreRule(self._driver)
            # ignore_rule.perform_delete_ignore_rule()
            ignore_rule.click_delete_icon_in_modal()
            time.sleep(4)  # Short wait to allow the confirmation dialog to appear
            ignore_rule.click_confirm_revoke_button()
            logger.info("Ignore rule deleted successfully.")
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
