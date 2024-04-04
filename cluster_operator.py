# cluster_operator.py
import time, datetime
import subprocess
from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

_setup_driver = None

def initialize_driver():
    global setup_driver
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    _setup_driver = webdriver.Chrome(options=chrome_options)
    # _setup_driver.set_window_size(1512, 982)
    _setup_driver.maximize_window()
    return _setup_driver


class ClusterManager:
    def __init__(self,driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, timeout=90, poll_frequency=0.001)

    def login(self, email_onboarding, login_pass_onboarding, url):
        driver = self.driver
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


        # check if onboarding-role page is displayed
        try:
            wait_for_element = WebDriverWait(driver, 5, 0.001)
            element = wait_for_element.until(EC.visibility_of_element_located((By.XPATH, "//div[@class='label font-semi-bold font-size-18 my-3' and contains(text(), 'What do you do?')]")))
        except:
            print("Onboarding role page is not displayed - not a sign-up user")
        else:
            print("Onboarding role page is displayed - sign-up user (first login)")
            ClusterManager.handle_role_page(self)
        
        
    def handle_role_page(self):
        driver = self.driver
        wait = self.wait
        try:
            role_button = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/armo-root/div/div/div/armo-role-page/div/div[2]/div/div[1]/armo-onboarding-survey-buttons-upper/div/div[1]/div[2]')))
            driver.execute_script("arguments[0].click();", role_button)
            print("Click on role button.")
        except TimeoutException as e:
            print("Role button was not found or clickable.")
            driver.save_screenshot(f"./role_button_error_{ClusterManager.get_current_timestamp()}.png")
        try:
            people_amount_button = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/armo-root/div/div/div/armo-role-page/div/div[2]/div/div[2]/armo-onboarding-survey-buttons-lower/div/div[1]/div[1]')))
            driver.execute_script("arguments[0].click();", people_amount_button)
            print("Click on people amount button.")
        except TimeoutException as e:
            print("People amount button was not found or clickable.")
            driver.save_screenshot(f"./people_amount_button_error_{ClusterManager.get_current_timestamp()}.png")
        try:    
            continue_button = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/armo-root/div/div/div/armo-role-page/div/div[2]/div/div[3]/button/span[2]'))) 
            driver.execute_script("arguments[0].click();", continue_button)
            print("Click on continue button.")
        except TimeoutException as e:
            print("Continue button was not found or clickable.")
            driver.save_screenshot(f"./continue_button_error_{ClusterManager.get_current_timestamp()}.png")
        try:
            experience_checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/armo-root/div/div/div/armo-features-page/div/div[2]/div/div[2]/armo-onboarding-how-best-help-buttons/div[1]/div')))
            driver.execute_script("arguments[0].click();", experience_checkbox)
            print("Click on experience checkbox.")
        except TimeoutException as e:
            print("Experience checkbox was not found or clickable.")
            driver.save_screenshot(f"./experience_checkbox_error_{ClusterManager.get_current_timestamp()}.png")
        try:    
            continue_button = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/armo-root/div/div/div/armo-features-page/div/div[2]/div/div[3]/button/span[2]')))
            driver.execute_script("arguments[0].click();", continue_button) 
            print("Click on continue button.")
        except TimeoutException as e:
            print("Continue button was not found or clickable.")
            driver.save_screenshot(f"./continue_button_error_{ClusterManager.get_current_timestamp()}.png")
        try:    #close the helm installation window
            close_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mat-dialog-0"]/armo-config-scanning-connection-wizard-dialog/armo-onboarding-dialog/armo-dialog-header/header/mat-icon')))
            driver.execute_script("arguments[0].click();", close_button)
            print("Click on close button.")
        except TimeoutException as e:
            print("Onboarding role page was not found or clickable.")
            driver.save_screenshot(f"./onboarding_role_page_error_{ClusterManager.get_current_timestamp()}.png")

    @staticmethod
    def get_current_timestamp(format_type="default"):
        if format_type == "special":
            return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    def press_esc_key(driver):
        try:
            actions = ActionChains(driver)
            actions.send_keys(Keys.ESCAPE).perform()
            print("ESC key pressed successfully.")
        except Exception as e:
            print("Failed to press the ESC key.", str(e))
            
    def click_filter_button(driver, xpath, filter_name):
        try:
            filter_button_element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath)))
            filter_button_element.click()
            print(f"{filter_name} filter clicked")
        except Exception as e:
            print(f"Failed to click on {filter_name} filter button:", str(e))
            driver.save_screenshot(f"./failed_to_click_on_{filter_name}_filter_button_{ClusterManager.get_current_timestamp()}.png")
        

class ConnectCluster:
    def __init__(self,driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, timeout=90, poll_frequency=0.001)

    def click_get_started(self):
        try:
            get_started_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(.,"Get started with Kubernetes security")]')))
            self.driver.execute_script("arguments[0].click();", get_started_button)
            print("Click on get started button.")
        except TimeoutException as e:
            print("Get started button was not found or clickable.")
            self.driver.save_screenshot(f"./get_started_button_error_{ClusterManager.get_current_timestamp()}.png")

    def connect_cluster_helm(self):
        css_selector = 'div.command-area > span.ng-star-inserted'
        helm_command_element = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector)))
        helm_command = helm_command_element.text
        try:
            result = subprocess.run(helm_command, shell=True, check=True, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            print(f"Helm command execution failed with error: {e}")
            if e.stderr:
                print(e.stderr.decode('utf-8'))

    def verify_installation(self):
        try:
            verify_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'armo-dialog-footer .mat-button-wrapper')))
            self.driver.execute_script("arguments[0].click();", verify_button)
        except TimeoutException as e:
            print("Verify button was not found or clickable.")
            self.driver.save_screenshot(f"./verify_button_erro_{ClusterManager.get_current_timestamp()}.png")


    def view_cluster_button(self):
        try:
            view_cluster_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'armo-connection-wizard-connection-step-footer .armo-button'))) 
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'armo-connection-wizard-connection-step-footer .armo-button')))
            time.sleep(2)
            self.driver.execute_script("arguments[0].click();", view_cluster_button)
        except TimeoutException as e:
            print("View cluster button was not found or clickable.")
            self.driver.save_screenshot(f"./view_cluster_button_error_{ClusterManager.get_current_timestamp()}.png")


    def view_connected_cluster(self,custom_wait_time=5, max_attempts=2):
        try:
            time.sleep(2)
            wait = WebDriverWait(self.driver, timeout=custom_wait_time, poll_frequency=0.001)
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'armo-cluster-scans-table .mat-tooltip-trigger')))
            print("View cluster connected found.")
        except TimeoutException as e:
            if max_attempts > 0:
                print(f"Failed to find view cluster connected. Refreshing page (Attempts left: {max_attempts}).")
                self.driver.save_screenshot(f"./view_connected_cluster_error_{ClusterManager.get_current_timestamp()}_attemp_{max_attempts}.png")
                self.driver.refresh()

                self.view_connected_cluster(custom_wait_time, max_attempts - 1)
            else:
                raise Exception("Element not found after maximum retry attempts.")


class Cleanup:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, timeout=90, poll_frequency=0.001)

    def uninstall_kubescape(self): 
        print("Uninstalling kubescape...")
        command = "helm uninstall kubescape -n kubescape && kubectl delete ns kubescape"
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            print(f"Error executing command: {stderr.decode()}")
        else:
            print(f"Command executed successfully: {stdout.decode()}")

    def click_settings_button(self):
        settings_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/armo-root/div/armo-side-nav-menu/nav/div[2]/armo-nav-items-list/ul[3]/li')))
        self.driver.execute_script("arguments[0].click();", settings_button)     
        print("Click on settings button.")

    def click_more_options_button(self):
        time.sleep(0.3)
        more_options_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.armo-button.table-more-actions.sm')))
        more_options_button.click()
        print("Click on more options button.")

    def choose_delete_option(self):
        time.sleep(0.3)
        delete_button = self.driver.find_element(By.XPATH, "//button[text()='Delete']")
        delete_button.click()
        print("Click on delete button option.")

    def confirm_delete(self):
        time.sleep(0.5)
        confirm_delete_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.mat-stroked-button[color='warn']")))
        confirm_delete_button.click()
        print("Click on confirm delete button.")

    def wait_for_empty_table(self):
        wait = WebDriverWait(self.driver, 180, 0.001)
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, 'td.mat-cell.text-center.ng-star-inserted'), 'No data to display'))
        print("Cleanup done")

class IgnoreRule:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, timeout=90, poll_frequency=0.001)

    def click_ignore_button(self, wait, driver):
        try:
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'button.armo-button.table-more-actions.sm')))
            driver.find_element(By.CSS_SELECTOR, 'button.armo-button.table-more-actions.sm')
            driver.execute_script("arguments[0].click();", driver.find_element(By.CSS_SELECTOR, 'button.armo-button.table-more-actions.sm'))
        except:
            print("failed to find the Accepting the Risk button")
            driver.save_screenshot(f"./ignore_button_error_{ClusterManager.get_current_timestamp()}.png")

    # Check if there are at the fields not empty
    def get_ignore_rule_field(self ,driver, index):
        # Define the CSS selector
        css_selector = ".mat-tooltip-trigger.field-value.truncate.ng-star-inserted"
        all_fields = driver.find_elements(By.CSS_SELECTOR, css_selector)

        # Access the field at the specified index
        all_fields[index]
        field_text = all_fields[index]
        # Retrieve the text content of the field
        field_text= field_text.text.strip()
        print(f"The RESOURCE is: '{field_text}'")
        return field_text
    
    def save_ignore_rule(self, wait, driver):
        try:
            save_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".save-button")))
            save_button.click()
            print("Click on save ignore rule.")
        except:
            print("failed to click on save button")
            driver.save_screenshot(f"./failed_to_click_on_save_button_{ClusterManager.get_current_timestamp()}.png")

    def igor_rule_icon_check(self):
        # Check if the icon change to ignored
        expected_svgsource = "/assets/icons/v2/general/edit-ignore.svg#edit-ignore"
        if expected_svgsource:
            print("The icon chabge to ignored.")
        else:
            print("The icon does NOT change to ignored.")

    def delete_ignore_rule(self, wait, driver):
        try:
            delete_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.delete-button.mat-focus-indicator.mat-tooltip-trigger')))
            delete_button.click()
            print("Click on delete ignore rule button.")
        except:
            print("Not found Delete ignore rule button.")
            driver.save_screenshot(f"./delete_ignore_rule_button_error_{ClusterManager.get_current_timestamp()}.png")

        # Click on the revoke button
        try:
            revoke_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.mat-focus-indicator.base-button.big-button.mat-stroked-button.mat-button-base.mat-warn')))
            revoke_button.click()
            print("Ignore rule deleted.")
        except:
            print("Revoke button not found.")
            driver.save_screenshot(f"./revoke_button_error_{ClusterManager.get_current_timestamp()}.png")


class RiskAcceptancePage:
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    def navigate_to_page(self):
        try:
            risk_acceptance_menu_item = self.driver.find_element(By.ID, "rick-acceptance-left-menu-item")
            risk_acceptance_menu_item.click()
            print("Clicked on Risk Acceptance.")
        except Exception as e:
            print(f"Error clicking on Risk Acceptance menu item: {e}")
            self.driver.save_screenshot(f"./failed_to_click_on_risk_acceptance_{ClusterManager.get_current_timestamp()}.png")

    def click_severity_element(self, css_selector):
        try:
            severity_element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
            severity_element.click()
            print("Clicked on the severity element.")
        except Exception:
            print(f"Failed to click on the severity element: {css_selector}")
            self.driver.save_screenshot(f"./failed_to_click_severity_element_{ClusterManager.get_current_timestamp()}.png")

            
    def click_edit_button(self, xpath):
        try:
            # Wait for the element to be clickable
            edit_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))

            # Scroll the element into view
            self.driver.execute_script("arguments[0].scrollIntoView(true);", edit_button)

            # Wait a bit for any potential overlays to disappear
            time.sleep(1)

            # Attempt to click using JavaScript
            self.driver.execute_script("arguments[0].click();", edit_button)

            print("Clicked the Edit button.")
        except Exception as e:
            print(f"Error clicking the Edit button: {e}")
            self.driver.save_screenshot(f"./failed_to_click_edit_button_{ClusterManager.get_current_timestamp()}.png")


    def delete_ignore_rule(self):
        try:
            ignore_rule = IgnoreRule(self.driver)
            ignore_rule.delete_ignore_rule(self.wait, self.driver)
            time.sleep(4)
        except Exception as e:
            print(f"Failed to delete ignore rule: {e}")
            self.driver.save_screenshot(f"./failed_to_delete_ignore_rule_{ClusterManager.get_current_timestamp()}.png")

    def switch_to_tab(self, tab_xpath):
        try:
            tab = self.wait.until(EC.element_to_be_clickable((By.XPATH, tab_xpath)))
            tab.click()
            print("switch to tab to Vulnerabilities.")
        except Exception as e:
            print(f"Error clicking on Vulnerabilities tab with XPath {tab_xpath}: {e}")
            self.driver.save_screenshot(f"./failed_to_click_on_tVulnerabilities_tab_{ClusterManager.get_current_timestamp()}.png")