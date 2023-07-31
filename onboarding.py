from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyperclip
import time
import subprocess

def setup_driver():
    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def login(driver, wait):
    url = "https://cloud.armosec.io/dashboard"
    driver.get(url)

    email_input_box = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="frontegg-login-box-container-default"]/div[1]/input')))
    # email_input_box.send_keys("uluhunhfkvfbcumwvo@cwmxc.com")
    email_input_box.send_keys("test.platform457@gmail.com")
    email_input_box.send_keys(Keys.ENTER)

    password_input_box = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/frontegg-app/div[2]/div[2]/input')))
    # password_input_box.send_keys("zxc123ZXC!")
    password_input_box.send_keys("Platformtest2!")
    password_input_box.send_keys(Keys.ENTER)

def click_get_started(driver, wait):
    get_started_button = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/armo-root/div/div/div/armo-home-page/armo-home-empty-state/armo-empty-state-page/main/section[1]/div/button/span[1]')))
    driver.execute_script("arguments[0].click();", get_started_button)

def copy_helm_command(driver,wait):
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'armo-copy-clipboard-panel .copy-button')))
    copy_button = driver.find_element(By.CSS_SELECTOR, 'armo-copy-clipboard-panel .copy-button')
    copy_button.click()
    return pyperclip.paste()

def execute_helm_command(helm_command):
    try:
        subprocess.run(helm_command, shell=True, check=True)
        print("Helm command executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Helm command execution failed with error: {e}")

def verify_installation(driver, wait):
    verify_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'armo-dialog-footer .mat-button-wrapper')))
    # driver.save_screenshot("verify_button.png")
    driver.execute_script("arguments[0].click();", verify_button)

def view_cluster(driver, wait):
    view_cluster_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'armo-connection-wizard-connection-step-footer .connection-step-button')))
    # driver.save_screenshot("view_cluster_button.png")
    driver.execute_script("arguments[0].click();", view_cluster_button)

def view_connected_cluster(driver, wait):
    delete_cluster_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'armo-cluster-scans-table .mat-tooltip-trigger')))
    # driver.save_screenshot("view_cluster_connected.png")


def main():
    start_time = time.time()
    driver = setup_driver()
    wait = WebDriverWait(driver, 125, 0.001)
    login(driver, wait)
    click_get_started(driver, wait)
    helm_command = copy_helm_command(driver, wait)
    execute_helm_command(helm_command)
    verify_installation(driver, wait)
    view_cluster(driver, wait)
    view_connected_cluster(driver, wait)
    
    onboarding_time = "{:.2f}".format(time.time() - start_time)
    print(f"{onboarding_time}")  
    # print(f"Total onboarding time: {onboarding_time} seconds")
    driver.quit()

if __name__ == "__main__":
    main()
