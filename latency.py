import os
import sys
import time, datetime
import subprocess
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

# Constants
PROD_URL = "https://cloud-ci-stg.cademo.cyberarmorsoft.com/compliance"
LOG_FILE = "./logs/latency_logs.csv"
EMAIL_LATENCY = os.environ['email_latency']
LOGIN_PASS_LATENCY = os.environ['login_pass_latency']


def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_window_size(1512, 982)
    return driver

def get_current_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def write_to_log(timestamp, latency, latency_without_login):
    with open(LOG_FILE, "a") as f:
        f.write(f"{timestamp},{latency},{latency_without_login}\n")

def handle_role_page(driver, wait):
    try:
        role_button = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/armo-root/div/div/div/armo-role-page/div/div[2]/div/div[1]/armo-onboarding-survey-buttons-upper/div/div[1]/div[2]')))
        driver.execute_script("arguments[0].click();", role_button)
        print("Click on role button.")
        driver.save_screenshot(f"./role_button_{get_current_timestamp()}.png")
    except TimeoutException as e:
        print("Role button was not found or clickable.")
        driver.save_screenshot(f"./role_button_error_{get_current_timestamp()}.png")
    try:
        people_amount_button = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/armo-root/div/div/div/armo-role-page/div/div[2]/div/div[2]/armo-onboarding-survey-buttons-lower/div/div[1]/div[1]')))
        driver.execute_script("arguments[0].click();", people_amount_button)
        print("Click on people amount button.")
    except TimeoutException as e:
        print("People amount button was not found or clickable.")
        driver.save_screenshot(f"./people_amount_button_error_{get_current_timestamp()}.png")
    try:    
        continue_button = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/armo-root/div/div/div/armo-role-page/div/div[2]/div/div[3]/button/span[2]'))) 
        driver.execute_script("arguments[0].click();", continue_button)
        print("Click on continue button.")
    except TimeoutException as e:
        print("Continue button was not found or clickable.")
        driver.save_screenshot(f"./continue_button_error_{get_current_timestamp()}.png")
    try:
        experience_checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/armo-root/div/div/div/armo-features-page/div/div[2]/div/div[2]/armo-onboarding-how-best-help-buttons/div[1]/div')))
        driver.execute_script("arguments[0].click();", experience_checkbox)
        print("Click on experience checkbox.")
    except TimeoutException as e:
        print("Experience checkbox was not found or clickable.")
        driver.save_screenshot(f"./experience_checkbox_error_{get_current_timestamp()}.png")
    try:    
        continue_button = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/armo-root/div/div/div/armo-features-page/div/div[2]/div/div[3]/button/span[2]')))
        driver.execute_script("arguments[0].click();", continue_button) 
        print("Click on continue button.")
    except TimeoutException as e:
        print("Continue button was not found or clickable.")
        driver.save_screenshot(f"./continue_button_error_{get_current_timestamp()}.png")
    try:    #close the helm installation window
        close_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mat-dialog-0"]/armo-config-scanning-connection-wizard-dialog/armo-onboarding-dialog/armo-dialog-header/header/mat-icon')))
        driver.execute_script("arguments[0].click();", close_button)
        print("Click on close button.")
    except TimeoutException as e:
        print("Onboarding role page was not found or clickable.")
        driver.save_screenshot(f"./onboarding_role_page_error_{get_current_timestamp()}.png")

def handle_login(driver, wait, email_latency, login_pass_latency, url):
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
        handle_role_page(driver, wait)

def navigate_to_dashboard(driver, wait):
    # Click on the compliance
    wait.until(EC.presence_of_element_located((By.ID, 'configuration-scanning-left-menu-item')))
    compliance = driver.find_element(By.ID, 'configuration-scanning-left-menu-item')
    driver.execute_script("arguments[0].click();", compliance)
    # take_screenshot(driver, "Click on the compliance")

    # Click on the cluster (the first one)
    wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/armo-root/div/div/div/armo-config-scanning-page/div[2]/armo-cluster-scans-table/table/tbody/tr[1]/td[2]')))
    cluster = driver.find_element(By.XPATH, '/html/body/armo-root/div/div/div/armo-config-scanning-page/div[2]/armo-cluster-scans-table/table/tbody/tr[1]/td[2]')
    driver.save_screenshot(f"./click_on_cluster_{get_current_timestamp()}.png")
    driver.execute_script("arguments[0].click();", cluster)
    

    # Click on the fix button
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="framework-control-table-failed-4"]/div/span[2]')))
    fix_button = driver.find_element(By.XPATH, '//*[@id="framework-control-table-failed-4"]/div/span[2]')
    driver.execute_script("arguments[0].click();", fix_button)
    # take_screenshot(driver, "Click on the fix button")

    # Wait until the rules list is visible
    wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/armo-root/div/div/div/armo-resources-ignore-rules-page/div[3]/armo-resources-ignore-rules-list/div/armo-resources-ignore-rules-list-with-namespace/table/thead/tr')))
    # take_screenshot(driver, "Wait until the rules list is visible")

    # Click on the fix button in the rules list
    wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/armo-root/div/div/div/armo-resources-ignore-rules-page/div[3]/armo-resources-ignore-rules-list/div/armo-resources-ignore-rules-list-with-namespace/table/tbody/tr[1]/td[3]/armo-resource-ignore-rules-cell/div/div[2]/armo-fix-button/armo-button/button')))
    # take_screenshot(driver, "Click on the fix button in the rules list")
    fix_button_on_remide = driver.find_element(By.XPATH, '/html/body/armo-root/div/div/div/armo-resources-ignore-rules-page/div[3]/armo-resources-ignore-rules-list/div/armo-resources-ignore-rules-list-with-namespace/table/tbody/tr[1]/td[3]/armo-resource-ignore-rules-cell/div/div[2]/armo-fix-button/armo-button/button')
    driver.execute_script("arguments[0].click();", fix_button_on_remide)
    window_handles = driver.window_handles
    driver.switch_to.window(window_handles[-1])

    # Wait until the yaml section is visible
    wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/armo-root/div/div/div/armo-failed-resource-page/armo-yaml-section/div/div/button[2]')))
    # take_screenshot(driver, "Wait until the yaml section is visible")
    # time.sleep(1)

def navigate_to_vulnerabilities(driver, wait):
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    # Click on the vulnerabilities page
    wait.until(EC.presence_of_element_located((By.ID, 'image-scanning-left-menu-item')))
    vulnerabilities = driver.find_element(By.ID, 'image-scanning-left-menu-item')
    driver.execute_script("arguments[0].click();", vulnerabilities)

    # Click on the first row
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="image-scanning-vulnerabilities-table-row-0"]/td[1]/span/span')))
    first_row = driver.find_element(By.XPATH, '//*[@id="image-scanning-vulnerabilities-table-row-0"]/td[1]/span/span')
    driver.execute_script("arguments[0].click();", first_row)
    
    #click on ignore of the first CVE
    first =wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/armo-root/div/div/div/armo-vce-report-page/div/armo-vce-table/table/tbody/tr[1]/td[9]/armo-ignore-rules-button/button')))
    # print("first yes")
    driver.execute_script("arguments[0].click();", first)
    # time.sleep(1)

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
    confirm_delete_button = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[5]/div[2]/div/mat-dialog-container/armo-notification/div[3]/button[2]')))
    driver.execute_script("arguments[0].click();", confirm_delete_button)


def wait_for_empty_table(driver):
    wait = WebDriverWait(driver, 180, 0.001)
    wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, 'td.mat-cell.text-center.ng-star-inserted'), 'No data to display'))


def perform_cleanup(driver, wait):
    max_retries = 2
    for _ in range(max_retries):
        try:
            print("Deleting cluster from ARMO platform\n"
                  "Clicking settings button...")
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

def measure_latency(driver, wait, email, login_pass, url):
    try:
        start_time = time.time() 
        handle_login(driver, wait, email, login_pass, url)
        login_time = time.time()
        navigate_to_dashboard(driver, wait)
        end_time_dashboard = time.time()
        navigate_to_vulnerabilities(driver, wait)
    except Exception as e:
        print(f"Latency test failed with error: {e}")
        print(traceback.format_exc())
        # print("performing cleanup...")
        # perform_cleanup(driver, wait)
        # driver.save_screenshot(f"latency_error_{get_current_timestamp()}.png")
        
    end_time = time.time()
    # perform_cleanup(driver, wait)
    login_latency = "{:.2f}".format(login_time - start_time)
    complaince_page_latency = "{:.2f}".format(end_time_dashboard - login_time)
    vulnerabilities_page_latency = "{:.2f}".format(end_time - end_time_dashboard)

    return login_latency, complaince_page_latency, vulnerabilities_page_latency


def main(url):
    driver = init_driver()
    wait = WebDriverWait(driver, 30, 0.001)

    login_latency, complaince_page_latency, vulnerabilities_page_latency = measure_latency(driver, wait, EMAIL_LATENCY, LOGIN_PASS_LATENCY, url)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # write_to_log(timestamp, latency, latency_without_login)

    print(f"""
Timestamp: {timestamp}
Login Latency: {login_latency} sec 
Latency to Compliance Page: {complaince_page_latency} sec 
Latency to Vulnerabilities Page: {vulnerabilities_page_latency} sec""")
    driver.quit()

if __name__ == '__main__':
    url = sys.argv[1] if len(sys.argv) > 1 else PROD_URL
    main(url)