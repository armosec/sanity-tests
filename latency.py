import os
import time, datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

url = "https://cloud.armosec.io/dashboard"
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)
driver.set_window_size(1512, 982)
wait = WebDriverWait(driver, 30, 0.001)


# def take_screenshot(driver, description):
#     timestamp = time.strftime("%Y%m%d-%H%M%S")
#     screenshot_name = f"{timestamp}_{description}.png"
#     driver.save_screenshot(screenshot_name)


def login(driver, wait, email_latency, login_pass_latency):
    driver.get(url)
    wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="frontegg-login-box-container-default"]/div[1]/input')))
    mail_input = driver.find_element(by=By.XPATH, value='//*[@id="frontegg-login-box-container-default"]/div[1]/input')
    mail_input.send_keys(email_latency)
    mail_input.send_keys(Keys.ENTER)
    wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/frontegg-app/div[2]/div[2]/input')))
    password_input = driver.find_element(by=By.XPATH, value='/html/body/frontegg-app/div[2]/div[2]/input')
    password_input.send_keys(login_pass_latency)
    password_input.send_keys(Keys.ENTER)

def navigate_to_dashboard(driver, wait):
    # Click on the compliance
    wait.until(EC.presence_of_element_located((By.ID, 'configuration-scanning-left-menu-item')))
    compliance = driver.find_element(By.ID, 'configuration-scanning-left-menu-item')
    driver.execute_script("arguments[0].click();", compliance)
    # take_screenshot(driver, "Click on the compliance")

    # Click on the cluster (the first one)
    wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/armo-root/div/div/div/armo-config-scanning-page/div[2]/armo-cluster-scans-table/table/tbody/tr[1]/td[2]')))
    cluster = driver.find_element(By.XPATH, '/html/body/armo-root/div/div/div/armo-config-scanning-page/div[2]/armo-cluster-scans-table/table/tbody/tr[1]/td[2]')
    driver.execute_script("arguments[0].click();", cluster)
    # take_screenshot(driver, "Click on the cluster")

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


def measure_latency(driver, wait, email_latency, login_pass_latency, url):
    start_time = time.time()
    login(driver, wait, email_latency, login_pass_latency)
    login_time = time.time()
    navigate_to_dashboard(driver, wait)
    end_time = time.time()
    latency_without_login = "{:.2f}".format(end_time - login_time)
    latency = "{:.2f}".format(end_time - start_time)
    return latency , latency_without_login


latency, latency_without_login = measure_latency(driver, wait, os.environ['email_latency'], os.environ['login_pass_latency'], url)
timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
with open("./logs/latency_logs.csv", "a") as f:
    f.write(f"{timestamp},{latency},{latency_without_login}\n")
    print(f"{timestamp}\n"
          f"Latency time: {latency} sec\n"
          f"Latency time without login: {latency_without_login} sec\n")
driver.quit()
