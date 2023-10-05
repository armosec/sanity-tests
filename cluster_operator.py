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

_setup_driver = None

def initialize_driver():
    global setup_driver
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    _setup_driver = webdriver.Chrome(options=chrome_options)
    _setup_driver.set_window_size(1512, 982)
    return _setup_driver
    

class ClusterManager:
    def __init__(self,driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, timeout=90, poll_frequency=0.001)

    def login(self, email_latency, login_pass_latency, url):
        driver = self.driver
        wait = self.wait
        driver.get(url)
        wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="frontegg-login-box-container-default"]/div[1]/input')))
        mail_input = driver.find_element(by=By.XPATH, value='//*[@id="frontegg-login-box-container-default"]/div[1]/input')
        mail_input.send_keys(email_latency)
        mail_input.send_keys(Keys.ENTER)
        wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/frontegg-app/div[2]/div[2]/input')))
        password_input = driver.find_element(by=By.XPATH, value='/html/body/frontegg-app/div[2]/div[2]/input')
        password_input.send_keys(login_pass_latency)
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
            # driver.save_screenshot(f"./role_button_{ClusterManager.get_current_timestamp()}.png")
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
    def get_current_timestamp():
        return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

class ConnectCluster:
    def __init__(self,driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, timeout=90, poll_frequency=0.001)

    def click_get_started(self):
        print("Click on get started button.")
        try:
            # get_started_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/armo-root/div/div/div/armo-home-page/armo-home-empty-state/armo-empty-state-page/main/section[1]/div/button/span[1]')))
            get_started_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/armo-root/div/div/div/armo-home-page/armo-home-empty-state/armo-empty-state-page/main/section[1]/div/armo-button/button')))
            self.driver.execute_script("arguments[0].click();", get_started_button)
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
            self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="mat-dialog-0"]/armo-config-scanning-connection-wizard-dialog/armo-onboarding-dialog/main/main/armo-connection-wizard-dialog-connection-step/div/img')))
            time.sleep(1)
            self.driver.execute_script("arguments[0].click();", view_cluster_button)
        except TimeoutException as e:
            print("View cluster button was not found or clickable.")
            self.driver.save_screenshot(f"./view_cluster_button_error_{ClusterManager.get_current_timestamp()}.png")



    def view_connected_cluster(self):
        try:
            self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'armo-cluster-scans-table .mat-tooltip-trigger')))
        except TimeoutException as e:
            print("Failed to find view cluster connected after retries. Refreshing page.")
            self.driver.save_screenshot(f"./view_connected_cluster_error_{ClusterManager.get_current_timestamp()}.png")
            self.driver.refresh()

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
        settings_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/armo-root/div/armo-side-nav-menu/nav/div[2]/armo-nav-items-list/div/ul/li/a/span')))
        self.driver.execute_script("arguments[0].click();", settings_button)
        self.driver.execute_script("arguments[0].click();", settings_button)
        print("Click on settings button.")

    def click_more_options_button(self):
        more_options_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/armo-root/div/div/div/div[2]/armo-clusters-page/armo-clusters-table/div/table/tbody/tr/td[9]/armo-row-options-button/button/mat-icon')))
        self.driver.execute_script("arguments[0].click();", more_options_button)
        print("Click on more options button.")

    def choose_delete_option(self):
        # delete_button_option = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mat-menu-panel-107"]/div/button[2]/div')))
        # delete_button_option = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mat-menu-panel-73"]/div/button[2]/div')))
        # self.driver.execute_script("arguments[0].click();", delete_button_option)
        delete_button = self.driver.find_element(By.XPATH, "//button[text()='Delete']")
        delete_button.click()
        print("Click on delete button option.")

    def confirm_delete(self):
        confirm_delete_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[5]/div[2]/div/mat-dialog-container/armo-notification/div[3]/button[2]')))
        self.driver.execute_script("arguments[0].click();", confirm_delete_button)
        print("Click on confirm delete button.")

    def wait_for_empty_table(self):
        wait = WebDriverWait(self.driver, 180, 0.001)
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, 'td.mat-cell.text-center.ng-star-inserted'), 'No data to display'))
        print("Cleanup done")