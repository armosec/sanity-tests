import os 
import subprocess
import time, datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC




def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def login(driver, wait, email_onboarding, login_pass_onboarding):
    url = "https://cloud.armosec.io/dashboard"
    driver.get(url)
    email_input_box = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="frontegg-login-box-container-default"]/div[1]/input')))
    email_input_box.send_keys(email_onboarding)
    email_input_box.send_keys(Keys.ENTER)
    password_input_box = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/frontegg-app/div[2]/div[2]/input')))
    password_input_box.send_keys(login_pass_onboarding)
    password_input_box.send_keys(Keys.ENTER)


def click_get_started(driver, wait):
    get_started_button = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/armo-root/div/div/div/armo-home-page/armo-home-empty-state/armo-empty-state-page/main/section[1]/div/button/span[1]')))
    driver.execute_script("arguments[0].click();", get_started_button)


def copy_helm_command(driver, wait):
    css_selector = 'div.command-area > span.ng-star-inserted'  # CSS selector targeting the Helm command
    helm_command_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector)))
    helm_command = helm_command_element.text  # Retrieve the text content of the Helm command
    return helm_command


def execute_helm_command(helm_command):
    try:
        result = subprocess.run(helm_command, shell=True, check=True, stderr=subprocess.PIPE)
        # print("Helm command executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Helm command execution failed with error: {e}")
        if e.stderr:  # Check if stderr is not None
            print(e.stderr.decode('utf-8'))  # Print stderr to see what went wrong


def verify_installation(driver, wait):
    verify_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'armo-dialog-footer .mat-button-wrapper')))
    # driver.save_screenshot("verify_button.png")
    driver.execute_script("arguments[0].click();", verify_button)
    

def view_cluster(driver, wait):
    try:
        view_cluster_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'armo-connection-wizard-connection-step-footer .connection-step-button')))
        # driver.save_screenshot("view_cluster_button.png")
        time.sleep(0.3)
        driver.execute_script("arguments[0].click();", view_cluster_button)
    except TimeoutException as e:
        print("View cluster button was not found or clickable.")
        # driver.save_screenshot("view_cluster_error.png")


def view_connected_cluster(driver, wait):
    try:
        delete_cluster_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'armo-cluster-scans-table .mat-tooltip-trigger')))
        # driver.save_screenshot("view_cluster_connected.png")
    except TimeoutException as e:
        print("View cluster connected button was not found or clickable.")
        # driver.save_screenshot("view_cluster_connected_error.png")

def click_settings_button(driver, wait):
    settings_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'li.d-flex.align-items-center.pl-4.pointer')))
    driver.execute_script("arguments[0].click();", settings_button)

def click_more_options_button(driver, wait):
    more_options_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'mat-icon.material-icons')))
    driver.execute_script("arguments[0].click();", more_options_button)

def choose_delete_option(driver, wait):
    delete_button_option = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.mat-menu-item')))
    driver.execute_script("arguments[0].click();", delete_button_option)

def confirm_delete(driver, wait):
    confirm_delete_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.mat-stroked-button.color-warn')))
    driver.execute_script("arguments[0].click();", confirm_delete_button)


def main():
    email_onboarding = os.environ.get('email_onboarding')
    login_pass_onboarding = os.environ.get('login_pass_onboarding')

    start_time = time.time()
    driver = setup_driver()
    wait = WebDriverWait(driver, 125, 0.001)
    login(driver, wait, email_onboarding, login_pass_onboarding)
    click_get_started(driver, wait)
    helm_command = copy_helm_command(driver, wait)
    execute_helm_command(helm_command)
    verify_installation(driver, wait)
    view_cluster(driver, wait)
    view_connected_cluster(driver, wait)
    
    onboarding_time = "{:.2f}".format(time.time() - start_time)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("./logs/onboarding_logs.csv", "a") as f:
        f.write(f"{timestamp},{onboarding_time}\n")
    # print(f"{timestamp},{onboarding_time}")

    click_settings_button(driver, wait)
    click_more_options_button(driver, wait)
    choose_delete_option(driver, wait)
    confirm_delete(driver, wait)
    wait_for_empty_table(driver, wait)
    driver.quit()

if __name__ == "__main__":
    main()