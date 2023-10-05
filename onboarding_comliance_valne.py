# test-onboarding.py
import os
import sys
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from cluster_operator import ClusterManager, ConnectCluster, Cleanup, initialize_driver
from selenium.webdriver.support.ui import WebDriverWait


def navigate_to_dashboard(driver, wait):
    # Click on the compliance
    try:
        wait.until(EC.presence_of_element_located((By.ID, 'configuration-scanning-left-menu-item')))
        compliance = driver.find_element(By.ID, 'configuration-scanning-left-menu-item')
        driver.execute_script("arguments[0].click();", compliance)
    except:
        print("failed to click on compliance")
        driver.save_screenshot(f"./failed_to_click_on_compliance_{ClusterManager.get_current_timestamp()}.png")

    # Click on the cluster (the first one)
    wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/armo-root/div/div/div/armo-config-scanning-page/div[2]/armo-cluster-scans-table/table/tbody/tr[1]/td[2]')))
    cluster = driver.find_element(By.XPATH, '/html/body/armo-root/div/div/div/armo-config-scanning-page/div[2]/armo-cluster-scans-table/table/tbody/tr[1]/td[2]')
    # driver.save_screenshot(f"./click_on_cluster_{ClusterManager.get_current_timestamp()}.png")
    driver.execute_script("arguments[0].click();", cluster)
    

    # Click on the fix button
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="configuration-scanning-controls-table"]/table/tbody/tr[2]/td[9]/armo-fix-button/armo-button')))
        fix_button = driver.find_element(By.XPATH, '//*[@id="configuration-scanning-controls-table"]/table/tbody/tr[2]/td[9]/armo-fix-button/armo-button')
        driver.execute_script("arguments[0].click();", fix_button)
    except:
        print("failed to click on fix button")
        driver.save_screenshot(f"./failed_to_click_on_fix_button_{ClusterManager.get_current_timestamp()}.png")

    # Wait until the rules list is visible
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/armo-root/div/div/div/armo-resources-ignore-rules-page/div[3]/armo-resources-ignore-rules-list/div/armo-resources-ignore-rules-list-with-namespace/table/thead/tr')))
    except:
        print("failed to find the rules list")
        driver.save_screenshot(f"./failed_to_find_the_rules_list_{ClusterManager.get_current_timestamp()}.png")

    # # Click on the fix button in the rules list
    # wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/armo-root/div/div/div/armo-vulnerabilities-page/div[2]/armo-vulnerabilities-table/table/tbody/tr[1]/td[1]')))
    # # take_screenshot(driver, "Click on the fix button in the rules list")
    # fix_button_on_remide = driver.find_element(By.XPATH, '/html/body/armo-root/div/div/div/armo-vulnerabilities-page/div[2]/armo-vulnerabilities-table/table/tbody/tr[1]/td[1]')
    # driver.execute_script("arguments[0].click();", fix_button_on_remide)
    # window_handles = driver.window_handles
    # driver.switch_to.window(window_handles[-1])

    # # Wait until the yaml section is visible
    # time.sleep(1)
    # wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/armo-root/div/div/div/armo-failed-resource-page/armo-yaml-section/div/div/button[2]')))
    # # take_screenshot(driver, "Wait until the yaml section is visible")
    

def navigate_to_vulnerabilities(driver, wait):
    # driver.close()
    # driver.switch_to.window(driver.window_handles[0])
    # Click on the vulnerabilities page
    wait.until(EC.presence_of_element_located((By.ID, 'image-scanning-left-menu-item')))
    vulnerabilities = driver.find_element(By.ID, 'image-scanning-left-menu-item')
    driver.execute_script("arguments[0].click();", vulnerabilities)

    # Click on the first row
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="image-scanning-vulnerabilities-table-row-0"]/td[1]/span/span')))
        first_row = driver.find_element(By.XPATH, '//*[@id="image-scanning-vulnerabilities-table-row-0"]/td[1]/span/span')
        driver.execute_script("arguments[0].click();", first_row)
    except:
        print("failed to click on the first row")
        driver.save_screenshot(f"./failed_to_click_on_the_first_row_on_vulne{ClusterManager.get_current_timestamp()}.png")
        

    #click on ignore of the first CVE
    try:
        first =wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/armo-root/div/div/div/armo-vce-report-page/div/armo-vce-table/table/tbody/tr[1]/td[9]/armo-ignore-rules-button/button')))                                    
        driver.execute_script("arguments[0].click();", first)
        time.sleep(0.5)
    except:
        print("failed to click on ignore of the first CVE")
        driver.save_screenshot(f"./failed_to_click_on_ignore_of_the_first_CVE_{ClusterManager.get_current_timestamp()}.png")

    # close the ignore window
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[5]/div[2]/div/mat-dialog-container/armo-cve-ignore-rule-dialog/div[1]/mat-icon')))
        close = driver.find_element(By.XPATH, '/html/body/div[5]/div[2]/div/mat-dialog-container/armo-cve-ignore-rule-dialog/div[1]/mat-icon')
        driver.execute_script("arguments[0].click();", close)
    except:
        print("failed to close the ignore window")
        driver.save_screenshot(f"./failed_to_close_the_ignore_window_{ClusterManager.get_current_timestamp()}.png") 

def perform_cleanup(driver):
    cleanup = Cleanup(driver)
    try:
        cleanup.uninstall_kubescape()
        cleanup.click_settings_button()   
        cleanup.click_more_options_button()
        cleanup.choose_delete_option()
        cleanup.confirm_delete()
        cleanup.wait_for_empty_table()

    except:
        print("Failed to perform cleanup")
        driver.save_screenshot(f"./failed_to_perform_cleanup_{ClusterManager.get_current_timestamp()}.png")
        exit(1) 
        
def main():
    # Assigning your variables
    email_onboarding = os.environ.get('email_onboarding')
    login_pass_onboarding = os.environ.get('login_pass_onboarding')
    prod_url = "https://cloud.armosec.io/dashboard"
    url = sys.argv[1] if len(sys.argv) > 1 else prod_url

    # Setup the driver
    driver = initialize_driver()
    wait = WebDriverWait(driver, 160, 0.001)

    try:
        # Login
        start_time = time.time()
        cluster_manager = ClusterManager(driver)
        cluster_manager.login(email_onboarding, login_pass_onboarding, url)
        login_time = time.time() - start_time

        # Connecting the cluster
        connect_cluster = ConnectCluster(driver)
        connect_cluster.click_get_started()
        connect_cluster.connect_cluster_helm()
        connect_cluster.verify_installation()
        connect_cluster.view_cluster_button()
        connect_cluster.view_connected_cluster()
        onboarding_time = time.time() - start_time

        # Navigating to dashboard
        comp_start_time = time.time()
        navigate_to_dashboard(driver, wait)
        compalince_time = time.time() - comp_start_time

        # Navigating to vulnerabilities 
        vul_start_time = time.time()
        navigate_to_vulnerabilities(driver, wait)
        vulnerabilities_time = time.time() - vul_start_time

        log_data = {
            'timestamp': ClusterManager.get_current_timestamp(),
            'login_time': f"{login_time:.2f}",
            'onboarding_time': f"{onboarding_time:.2f}",
            'onboarding_time_excluding_login': f"{(onboarding_time - login_time):.2f}",
            'compliance_time': f"{compalince_time:.2f}",
            'vulnerabilities_time': f"{vulnerabilities_time:.2f}"
        }
        print(f"Timestamp: {log_data['timestamp']}\n"
              f"Login Time: {log_data['login_time']}\n"
              f"Onboarding Time: {log_data['onboarding_time']}\n"
              f"Onboarding Time (Excluding Login): {log_data['onboarding_time_excluding_login']}\n"
              f"Compliance Time: {log_data['compliance_time']}\n"
              f"Vulnerabilities Time: {log_data['vulnerabilities_time']}\n")


        with open("./logs/onboarding_logs.csv", "a") as f:
            f.write(','.join(str(log_data[key]) for key in log_data) + '\n')  
            
    finally:
        # Cleanup
        perform_cleanup(driver)
        driver.quit()        

if __name__ == "__main__":
    main()
