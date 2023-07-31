from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import os 
import subprocess

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
    # Replace the following string with the correct CSS selector for the element containing the Helm command
    css_selector_for_helm_command = '.some-class #some-id'
    helm_command_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector_for_helm_command)))

    # Use JavaScript to get the text content of the element
    helm_command = driver.execute_script("return arguments[0].textContent;", helm_command_element)

    print(f"Copied helm command: {helm_command.strip()}")  # Print the command
    return helm_command.strip()


def copy_helm_command(driver, wait):
    css_selector = 'div.command-area > span.ng-star-inserted'  # CSS selector targeting the Helm command
    helm_command_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector)))
    helm_command = helm_command_element.text  # Retrieve the text content of the Helm command
    return helm_command

def execute_helm_command(helm_command):
    # print(f"Helm command: {helm_command}")
    try:
        result = subprocess.run(helm_command, shell=True, check=True, stderr=subprocess.PIPE)
        print("Helm command executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Helm command execution failed with error: {e}")
        if e.stderr:  # Check if stderr is not None
            print(e.stderr.decode('utf-8'))  # Print stderr to see what went wrong



def verify_installation(driver, wait):
    verify_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'armo-dialog-footer .mat-button-wrapper')))
    driver.save_screenshot("verify_button.png")
    driver.execute_script("arguments[0].click();", verify_button)
    

def view_cluster(driver, wait):
    try:
        view_cluster_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'armo-connection-wizard-connection-step-footer .connection-step-button')))
        driver.save_screenshot("view_cluster_button.png")
        time.sleep(0.3)
        driver.execute_script("arguments[0].click();", view_cluster_button)
    except TimeoutException as e:
        print("View cluster button was not found or clickable.")
        driver.save_screenshot("view_cluster_error.png")


def view_connected_cluster(driver, wait):
    try:
        delete_cluster_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'armo-cluster-scans-table .mat-tooltip-trigger')))
        driver.save_screenshot("view_cluster_connected.png")
    except TimeoutException as e:
        print("View cluster connected button was not found or clickable.")
        driver.save_screenshot("view_cluster_connected_error.png")

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
    # print(f"Total onboarding time: {onboarding_time} seconds")
    print(f"{onboarding_time}")  
    driver.quit()

if __name__ == "__main__":
    main()
