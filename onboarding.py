import os
import sys
import subprocess
import traceback
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
    driver.set_window_size(1512, 982)
    return driver

def get_current_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")


def login(driver, wait, email_onboarding, login_pass_onboarding, url):
    # url = "https://cloud.armosec.io/dashboard"
    driver.get(url)
    email_input_box = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="frontegg-login-box-container-default"]/div[1]/input')))
    email_input_box.send_keys(email_onboarding)
    email_input_box.send_keys(Keys.ENTER)
    password_input_box = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/frontegg-app/div[2]/div[2]/input')))
    password_input_box.send_keys(login_pass_onboarding)
    password_input_box.send_keys(Keys.ENTER)
    # check if onboarding-role page is displayed
    try:
        element = wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@class='label font-semi-bold font-size-18 my-3' and contains(text(), 'What do you do?')]")))
    except:
        print("Onboarding role page is not displayed - not a sign up user")

        
def role_page(driver, wait):
    role_button = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/armo-root/div/div/div/armo-role-page/div/div[2]/div/div[1]/armo-onboarding-survey-buttons-upper/div/div[1]/div[1]')))
    driver.execute_script("arguments[0].click();", role_button)
    people_amount_button = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/armo-root/div/div/div/armo-role-page/div/div[2]/div/div[2]/armo-onboarding-survey-buttons-lower/div/div[1]/div[1]')))
    driver.execute_script("arguments[0].click();", people_amount_button)
    continue_button = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/armo-root/div/div/div/armo-role-page/div/div[2]/div/div[3]/button/span[2]'))) 
    driver.execute_script("arguments[0].click();", continue_button)
    experience_checkbox = driver.find_element_by_id('mat-checkbox-2-input')
    experience_checkbox.click()
    continue_button = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/armo-root/div/div/div/armo-features-page/div/div[2]/div/div[3]/button/span[2]')))
    driver.execute_script("arguments[0].click();", continue_button) 
    #close the helm installation window
    close_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mat-dialog-0"]/armo-config-scanning-connection-wizard-dialog/armo-onboarding-dialog/armo-dialog-header/mat-icon')))
    driver.execute_script("arguments[0].click();", close_button) 


def click_get_started(driver, wait):
    get_started_button = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/armo-root/div/div/div/armo-home-page/armo-home-empty-state/armo-empty-state-page/main/section[1]/div/button/span[1]')))
    driver.execute_script("arguments[0].click();", get_started_button)


def copy_helm_command(driver, wait):
    css_selector = 'div.command-area > span.ng-star-inserted'
    helm_command_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector)))
    helm_command = helm_command_element.text
    return helm_command


def execute_helm_command(helm_command):
    try:
        result = subprocess.run(helm_command, shell=True, check=True, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(f"Helm command execution failed with error: {e}")
        if e.stderr:
            print(e.stderr.decode('utf-8'))


def verify_installation(driver, wait):
    try:
        verify_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'armo-dialog-footer .mat-button-wrapper')))
        driver.execute_script("arguments[0].click();", verify_button)
    except TimeoutException as e:
        print("Verify-button was not found or clickable.")
        driver.save_screenshot(f"./verify_button_erro_{get_current_timestamp()}.png")


def view_cluster_button(driver, wait):
    try:
        view_cluster_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'armo-connection-wizard-connection-step-footer .armo-button'))) 
        wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="mat-dialog-0"]/armo-config-scanning-connection-wizard-dialog/armo-onboarding-dialog/main/main/armo-connection-wizard-dialog-connection-step/div/img')))
        time.sleep(1)
        driver.execute_script("arguments[0].click();", view_cluster_button)
    except TimeoutException as e:
        print("View cluster button was not found or clickable.")
        driver.save_screenshot(f"./view_cluster_button_error_{get_current_timestamp()}.png")
        


def view_connected_cluster(driver, wait):
    wait = WebDriverWait(driver, 30, 0.001)
    try:
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'armo-cluster-scans-table .mat-tooltip-trigger')))
    except TimeoutException as e:
        print("Failed to find view cluster connected after retries. Refreshing page.")
        driver.save_screenshot(f"./view_connected_cluster_error_{get_current_timestamp()}.png")
        driver.refresh()


def uninstall_kubescape():
    print("Uninstalling kubescape...")
    command = "helm uninstall kubescape -n kubescape && kubectl delete ns kubescape"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        print(f"Error executing command: {stderr.decode()}")
    else:
        print(f"Command executed successfully: {stdout.decode()}")


def click_settings_button(driver, wait):
    settings_button = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/armo-root/div/armo-side-nav-menu/nav/div[2]/armo-nav-items-list/div/ul/li/a/span')))
    driver.execute_script("arguments[0].click();", settings_button)


def click_more_options_button(driver, wait):
    more_options_button = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/armo-root/div/div/div/div[2]/armo-clusters-page/armo-clusters-table/div/table/tbody/tr/td[9]/armo-row-options-button/button/mat-icon')))
    driver.execute_script("arguments[0].click();", more_options_button)


def choose_delete_option(driver, wait):
    delete_button_option = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[5]/div[2]/div/div/div/button[2]/div')))
    driver.execute_script("arguments[0].click();", delete_button_option)


def confirm_delete(driver, wait):
    confirm_delete_button = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[6]/div[3]/div/mat-dialog-container/armo-notification/div[3]/button[2]')))
    driver.execute_script("arguments[0].click();", confirm_delete_button)


def wait_for_empty_table(driver):
    wait = WebDriverWait(driver, 180, 0.001)
    wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, 'td.mat-cell.text-center.ng-star-inserted'), 'No data to display'))


def perform_cleanup(driver, wait):
    max_retries = 2
    for _ in range(max_retries):
        try:
            print("Clicking settings button...")
            click_settings_button(driver, wait)

            print("Clicking more options button...")
            click_more_options_button(driver, wait)

            print("Choosing delete option...")
            choose_delete_option(driver, wait)

            print("Confirming delete...")
            confirm_delete(driver, wait)

            print("Waiting for empty table...")
            wait_for_empty_table(driver)
            break
        except Exception as e:
            print(f"Cleanup cluster attempt {max_retries} failed with error:")
            print("Stack trace:")
            print(traceback.format_exc())
                                                
            cleanup_error_screenshot = f"./cleanup_err_{get_current_timestamp()}.png"
            print(f"Saving screenshot - cleanup_err_{get_current_timestamp()}.png")
            driver.save_screenshot(cleanup_error_screenshot)



def main():
    email_onboarding = os.environ.get('email_onboarding')
    login_pass_onboarding = os.environ.get('login_pass_onboarding')
    prod_url = "https://cloud.armosec.io/dashboard"
    url = sys.argv[1] if len(sys.argv) > 1 else prod_url

    start_time = time.time()
    driver = setup_driver()
    wait = WebDriverWait(driver, 90, 0.001)
    login(driver, wait, email_onboarding, login_pass_onboarding, url)
    login_time = time.time()
    click_get_started(driver, wait)
    helm_command = copy_helm_command(driver, wait)
    execute_helm_command(helm_command)
    verify_installation(driver, wait)
    view_cluster_button(driver, wait)
    view_connected_cluster(driver, wait)
    end_time = time.time()
    uninstall_kubescape()
    perform_cleanup(driver, wait)
    driver.quit()
    
    onboarding_time = "{:.2f}".format(end_time - start_time)
    lonboarding_time_without_login = "{:.2f}".format(end_time - login_time)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("./logs/onboarding_logs.csv", "a") as f:
        f.write(f"{timestamp},{onboarding_time},{lonboarding_time_without_login}\n")
    print(f"{timestamp}\n"
          f"Onboarding time: {onboarding_time}\n"
          f"Onboarding time without login: {lonboarding_time_without_login}\n")
    


if __name__ == "__main__":
    main()
