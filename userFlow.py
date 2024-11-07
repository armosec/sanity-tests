# test-onboarding.py
import os
import sys
import time
import subprocess
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from cluster_operator import ClusterManager, ConnectCluster,Cleanup, IgnoreRule ,RiskAcceptancePage, initialize_driver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import TimeoutException



def navigate_to_dashboard(driver, wait):
        
    # Click on the compliance
    try:
        wait = WebDriverWait(driver, 10, 0.001)
        wait.until(EC.presence_of_element_located((By.ID, 'configuration-scanning-left-menu-item')))
        compliance = driver.find_element(By.ID, 'configuration-scanning-left-menu-item')
        driver.execute_script("arguments[0].click();", compliance)
        print
    except:
        print("failed to click on compliance")
        driver.save_screenshot(f"./failed_to_click_on_compliance_{ClusterManager.get_current_timestamp()}.png")
    
    # Click on the cluster (the first one) 
    time.sleep(1)
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/armo-root/div/div/div/armo-config-scanning-page/div[2]/armo-cluster-scans-table/table/tbody/tr[1]/td[2]')))
        cluster = driver.find_element(By.XPATH, '/html/body/armo-root/div/div/div/armo-config-scanning-page/div[2]/armo-cluster-scans-table/table/tbody/tr[1]/td[2]')
        driver.execute_script("arguments[0].click();", cluster)
        print("First Cluster selected")
    except:
        print("failed to click on the cluster")
        driver.save_screenshot(f"./failed_to_click_on_the_cluster_{ClusterManager.get_current_timestamp()}.png")
    
    time.sleep(1)
    # click on ID filter
    try:
        id_button = "//button[.//span[contains(text(), 'Control ID')]]"
        id_element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, id_button)))
        id_element.click()
        print("ID filter button clicked")
    except:
        print("failed to click on ID filter button")
        driver.save_screenshot(f"./failed_to_click_on_ID_filter_button_{ClusterManager.get_current_timestamp()}.png")

    # set 271 for C-0271 control
    try:
        time.sleep(0.5)
        input_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.search-input")))
        input_element.clear()
        input_element.send_keys("271")
        print("271 for C-0271 control set")
    except: 
        print("failed to set 271 for C-00271 control")
        driver.save_screenshot(f"./failed_to_set_271_for_C-00271_control_{ClusterManager.get_current_timestamp()}.png")
    
    # choose the C-0271 control
    try:
        # Wait for the checkbox to be present
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".mat-checkbox"))
        )

        # Execute JavaScript to toggle the checkbox
        # Find the checkbox by its unique attribute, like a label or aria-label
        script = """
        let checkboxes = document.querySelectorAll('.mat-checkbox');
        for (let box of checkboxes) {
            let label = box.querySelector('.value.truncate');
            if (label && label.textContent.includes('C-0271')) {
                box.click(); // Toggles the checkbox
                break; // Assuming you only need to click the first matching checkbox
            }
        }
        """
        driver.execute_script(script)
        print("Checkbox of C-0271 clicked.")
    except Exception as e:
        print("Failed to click the checkbox.", str(e))
        driver.save_screenshot(f"./failed_to_click_c-0271_checkbox_{ClusterManager.get_current_timestamp()}.png")


    # click on the esc button
    ClusterManager.press_esc_key(driver)

    # # Click on the fix button
    try:
        time.sleep(0.5)                                        
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="configuration-scanning-controls-table"]/table/tbody/tr/td[10]/armo-fix-button/armo-button/button')))
        fix_button = driver.find_element(By.XPATH, '//*[@id="configuration-scanning-controls-table"]/table/tbody/tr/td[10]/armo-fix-button/armo-button/button')
        driver.execute_script("arguments[0].click();", fix_button)
        print("Fix button clicked")
    except:
        print("failed to click on fix button")
        driver.save_screenshot(f"./failed_to_click_on_fix_button_{ClusterManager.get_current_timestamp()}.png")
    
    # Wait until the side by side remediation page is visible
    WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) == 2)
    driver.switch_to.window(driver.window_handles[1])
    try:
        time.sleep(4)
        wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/armo-root/div/div/div/armo-side-by-side-remediation-page/div/armo-comparison-wrapper/div/div/div[1]/div/p')))
        parent_selector = "div.row-container.yaml-code-row"
        parent_element = driver.find_element(By.CSS_SELECTOR, parent_selector)

        # Find all armo-yaml-code elements within the parent element
        armo_yaml_code_elements = parent_element.find_elements(By.CSS_SELECTOR, "armo-yaml-code")
    except:
        print("side by side remediation page is not visible")
        driver.save_screenshot(f"./SBS_page_not_loaded_{ClusterManager.get_current_timestamp()}.png")

    # Check if there are exactly 2 child elements
    if len(armo_yaml_code_elements) == 2:
        # Count the number of rows in each armo-yaml-code element
        rows_count = [len(elm.find_elements(By.TAG_NAME, "tr")) for elm in armo_yaml_code_elements]

        # Compare the row counts of the two elements
        if rows_count[0] == rows_count[1]:
            print(f"Both armo-yaml-code elements have the same number of rows: {rows_count[0]} rows.")
        else:
            print(f"The armo-yaml-code elements have different numbers of rows: {rows_count[0]} and {rows_count[1]} rows.")

    else:
        print(f"The element contains {len(armo_yaml_code_elements)} armo-yaml-code child elements, not 2.")
    time.sleep(2)
    driver.switch_to.window(driver.window_handles[0])

    # Click on the resourse link (failed and accepted)
    try:
        resourse_link= wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="framework-control-table-failed-0"]/div/armo-router-link/a/armo-button/button')))
        resourse_link.click()                                          
    except: 
        print("failed to click on resourse link")
        driver.save_screenshot(f"./failed_to_click_on_the_resourse_link_{ClusterManager.get_current_timestamp()}.png")    
    
    # Wait until the table of the esourse is present  
    try:
        wait = WebDriverWait(driver, 60, 0.001)
        # wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "armo-resources-ignore-rules-list.ng-star-inserted")))
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "armo-button button.armo-button.primary.sm")))
        print("Table of the resourse is present")
    except:
        print("Table of the resourse is not present")
        driver.save_screenshot(f"./failed_to_find_the_resourse_table_{ClusterManager.get_current_timestamp()}.png")
    
    time.sleep(1)
    ignore_rule = IgnoreRule(driver)
    ignore_rule.click_ignore_button(wait, driver)
    time.sleep(2)
    resource_name = ignore_rule.get_ignore_rule_field(driver, 2)
    print(f"resource name: {resource_name}")
    time.sleep(1)
    ignore_rule.save_ignore_rule(wait, driver) 
    time.sleep(3)
    ignore_rule.igor_rule_icon_check()
    return resource_name



    
def navigate_to_vulnerabilities(driver, wait):
    # Click on the vulnerabilities page
    vulnerabilities = driver.find_element(By.ID, 'image-scanning-left-menu-item')
    driver.execute_script("arguments[0].click();", vulnerabilities)
    print("Vulnerabilities clicked")
    
    cluster_manager = ClusterManager(driver)    
    print("waiting for the vulnerabilities page to be displayed - 1 min")
    time.sleep(60)
    # Click on the Workloads tab
    cluster_manager.click_menu_item_vuln_view("Workloads")
    
    # Click on the namespace filter
    name_space = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/armo-root/div/div/div/armo-workloads-page/div[2]/armo-table-filters/armo-created-filters-list/div/armo-multi-select-filter[2]/armo-common-trigger-button/armo-button/button')))
    cluster_manager.click_button_by_text("Namespace")
    print("Namespace filter clicked")
    
    # Click on the all namespaces (select all)
    select_all_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(@class, 'color-blue') and contains(text(), 'Select all')]")))
    driver.execute_script("arguments[0].click();", select_all_button)
    print("All namespaces selected")
    
    time.sleep(1)
    # Verify that all namespaces are selected
    checkboxes_container_xpath = '//ul[@class="m-0 px-0 pt-1 font-size-14"]'

    # Wait for the container of checkboxes to ensure it's loaded
    checkboxes_container = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, checkboxes_container_xpath))
    )

    # Find all 'mat-checkbox' elements within the container
    checkbox_elements = checkboxes_container.find_elements(By.XPATH, ".//mat-checkbox")

    # Initialize a list to hold the names of selected checkboxes
    selected_checkbox_names = []

    # Loop through each 'mat-checkbox' element
    for checkbox_element in checkbox_elements:
        # The actual checkbox input element
        checkbox = checkbox_element.find_element(By.XPATH, ".//input[@type='checkbox']")
        # Check if the checkbox is selected
        if checkbox.is_selected():
            # The span that contains the text label
            label_span = checkbox_element.find_element(By.XPATH, ".//span[@class='mat-tooltip-trigger value truncate']")
            # Append the text label to the list if it's not empty
            label_text = label_span.text.strip()
            if label_text:
                selected_checkbox_names.append(label_text)
            else:
                # If the text is empty, there might be a tooltip attribute containing the label
                label_text = label_span.get_attribute('aria-describedby')
                if label_text:
                    # Extract the label from the tooltip or another attribute if necessary
                    # This is a placeholder and may need adjustment based on actual attribute values
                    tooltip_text = label_span.get_attribute('aria-label') or label_span.get_attribute('title')
                    selected_checkbox_names.append(tooltip_text)

    # Print the names of all selected checkboxes
    print("Selected checkboxes:", selected_checkbox_names)

    # Locate the "Clear" button and click it
    clear_button = driver.find_element(By.XPATH, "//span[contains(@class, 'color-blue') and contains(@class, 'font-size-12') and contains(text(), 'Clear')]")
    clear_button.click()
    print("All checkboxes cleared")
    
    time.sleep(1)
    
    # Now verify that all checkboxes are unselected
    # Re-use the same container XPath as before
    checkboxes_container = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, checkboxes_container_xpath))
    )
    
    # Find all checkboxes within the container again
    checkboxes = checkboxes_container.find_elements(By.XPATH, ".//mat-checkbox//input[@type='checkbox']")
    
    # Verify all checkboxes are unselected
    none_selected = all(not checkbox.is_selected() for checkbox in checkboxes)
    
    print("All checkboxes unselected:", none_selected)

    # click on the esc button
    ClusterManager.press_esc_key(driver)

    # Click name space filter
    time.sleep(1)
    try:
        # name_space = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/armo-root/div/div/div/armo-workloads-page/div[2]/armo-table-filters/armo-created-filters-list/div/armo-multi-select-filter[2]/armo-common-trigger-button/armo-button/button')))
        # name_space.click()
        cluster_manager.click_button_by_text("Namespace")
        print("Namespace filter clicked")
    except:
        print("failed to click on namespace filter")
        driver.save_screenshot(f"./failed_to_click_on_namespace_filter_{ClusterManager.get_current_timestamp()}.png")

    # Coose the namespace -default 
    try:
        time.sleep(1)
        checkbox_label_xpath = "//span[contains(@class, 'mat-checkbox-label') and .//span[contains(text(), 'default')]]"
        checkbox_label = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, checkbox_label_xpath)))
        time.sleep(0.5)
        checkbox_label.click()
        print("namespace selected: default ") 
    except:
        print("failed to select the namespace")
        driver.save_screenshot(f"./failed_to_select_the_namespace_{ClusterManager.get_current_timestamp()}.png")


    # click on the esc button
    ClusterManager.press_esc_key(driver)
    # driver.refresh() # refresh the page to get the vulnerabilities - test
    # Click on the severity filter
    try:
        time.sleep(3)
        # Wait until the element is clickable
        high_filter = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, "//div[@class='severity-background']")))
        high_filter[1].click()
        print("Clicked on the high severity fiter")
    except Exception as e:
        print("failed to click on the high severity fiter")
        print(str(e))
        driver.save_screenshot(f"./failed_to_click_on_high_severity_filter_{ClusterManager.get_current_timestamp()}.png")

    # Creat Ignore rule
    time.sleep(1)
    ignore_rule = IgnoreRule(driver)
    ignore_rule.click_ignore_button(wait, driver)
    print("Clicked on the 'Accept Risk' button")
    time.sleep(1)
    container_name = ignore_rule.get_ignore_rule_field(driver, 3)
    print(f"container name: {container_name}")
    time.sleep(1)
    ignore_rule.save_ignore_rule(wait, driver) 
    time.sleep(3)
    ignore_rule.igor_rule_icon_check()
    return container_name

def navigate_to_network_policy(driver, wait):
    
    print("Reset pods in the 'default' namespace...")        
    ClusterManager.run_shell_command("kubectl delete pods -n default --all")
        
    print("waiting for the network policy page to be displayed - 3 min")
    time.sleep(180)
    print("View generated network policies:")
    ClusterManager.run_shell_command("kubectl get generatednetworkpolicies -A")
     
    # Click on the network policy page
    network_policy = driver.find_element(By.ID, 'network-policy-left-menu-item')
    driver.execute_script("arguments[0].click();", network_policy)
    print("go to Network policy page")

    # Click on the status filter
    try:
        status_button = "//button[contains(., 'Status')]"
        status_button_element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, status_button)))
        status_button_element.click()
        print("status filter clicked")
    except:
        print("failed to click on status filter button")
        driver.save_screenshot(f"./failed_to_click_on_status_filter_button_{ClusterManager.get_current_timestamp()}.png")
        
    # Click on the 'NP is recommended' checkbox  
    time.sleep(0.5)
    try:
        label_for_checkbox = driver.find_element(By.XPATH, "//div[contains(@class,'cdk-overlay-pane')]//span[contains(text(), 'Network policy is recommended')]/ancestor::label")
        label_for_checkbox.click()   
        print("clicked NP is recommende checkbox")
    except Exception as e:
        print(f"Failed to click on 'Network policy is recommended' checkbox: {e}")
        driver.save_screenshot(f"./failed_to_click_on_the_NP_checkbox_{ClusterManager.get_current_timestamp()}.png")
        
    # click on the esc button
    ClusterManager.press_esc_key(driver)
    
    try:
        time.sleep(1)
        label_for_checkbox = driver.find_element(By.XPATH, "//mat-checkbox[@data-test-id='checkbox']")
        label_for_checkbox.click()
        print("Clicked on the first workload checkbox.")
    except Exception as e:
        print(f"Failed to click on the workload CHECKBOX: {str(e)}")
        driver.save_screenshot(f"./failed_to_find_the_first_workload_{ClusterManager.get_current_timestamp()}.png")
        

    # Click the 'Generate' button
    try:
        time.sleep(1)
        generate_button = driver.find_element(By.XPATH, "/html/body/armo-root/div/div/div/armo-network-policy-page/div[4]/armo-workloads-table/div/div/armo-button/button")
        generate_button.click()
        print("Generate button clicked")
    except:
        print("failed to click on Generate button")
        driver.save_screenshot(f"./failed_to_click_on_generate_button_{ClusterManager.get_current_timestamp()}.png")
        
    # Open the NP   
    try:
        time.sleep(2)
        button =  wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "button.armo-button.table-secondary.sm svg use[href='assets/icons/v2/arrows/chevron-right.svg#chevron-right']")))
        driver.execute_script("""
        var svg = arguments[0];
        var event = new MouseEvent('click', {
            'view': window,
            'bubbles': true,
            'cancelable': true
        });
        svg.dispatchEvent(event);
        """, button)
     
        print("NP opened")
    except:
        print("failed to open NP")
        driver.save_screenshot(f"./failed_to_open_NP_{ClusterManager.get_current_timestamp()}.png")
        
    # Verify the NP is displayed
    overlay_selector = "cdk-overlay-pane"
    timeout = 5
    try:
        # Wait for the overlay to be visible
        overlay = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((By.CLASS_NAME, overlay_selector))
        )
        print("Overlay is visible.")
        table = overlay.find_element(By.TAG_NAME, "table")
        # Iterating over each row in the table
        rows = table.find_elements(By.TAG_NAME, "tr")
        for row in rows:
            row_text = row.text
            # Check if row contains text indicating a Network Policy
            if "kind: NetworkPolicy" in row_text:
                print(f"Network Policy found  row: {row_text}")
                return  # Stop after finding the first NP
            else:
                print("NP not displayed.")
                driver.save_screenshot(f"./NP_not_displayed_{ClusterManager.get_current_timestamp()}.png")
                
    except TimeoutException:
        print(f"Timeout: Overlay not visible after {timeout} seconds.")
    except NoSuchElementException:
        print("No table within the overlay was found containing NP indication.")

    # Click on the 'exit' button
    try:
        exit_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "svg.armo-icon.lg.ng-star-inserted use[href*='close.svg#close']")))
        driver.execute_script("""
        var svg = arguments[0];
        var event = new MouseEvent('click', {
            'view': window,
            'bubbles': true,
            'cancelable': true
        });
        svg.dispatchEvent(event);
        """, exit_button)
        print("Exit button clicked")
    except:
        print("failed to click on the exit button")
        driver.save_screenshot(f"./failed_to_click_on_exit_button_{ClusterManager.get_current_timestamp()}.png")


def risk_acceptance_page(driver, wait):
    risk_acceptance = RiskAcceptancePage(driver, wait)
    time.sleep(3)
    risk_acceptance.navigate_to_page()
    print("Navigated to Risk Acceptance page")
    time.sleep(1)
    risk_acceptance.switch_tab("Vulnerabilities")
    risk_acceptance.click_severity_element("td.mat-cell.mat-column-vulnerabilities-0-severityScore")
    time.sleep(1)
    risk_acceptance.click_edit_button("//armo-button[@buttontype='primary']//button[text()='Edit']")
    time.sleep(2.5)
    risk_acceptance.delete_ignore_rule()
    time.sleep(3)

    risk_acceptance.switch_tab("Compliance")
    time.sleep(1)
    risk_acceptance.click_severity_element("td.mat-cell.cdk-column-posturePolicies-0-severityScore")
    time.sleep(1)
    risk_acceptance.click_edit_button("//armo-button[@buttontype='primary']//button[text()='Edit']")
    time.sleep(2.5)
    risk_acceptance.delete_ignore_rule()
    time.sleep(3)


def verify_and_click_description(index, wait, driver):
    try:
        # Re-locate descriptions inside the function to avoid stale references
        descriptions = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-test-id='description']")))

        # Click the description at the specified index
        descriptions[index].click()

        # Wait for the element to be visible after click
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//th[contains(@class, 'cdk-column-id') or contains(@class, 'cdk-column-name')]")))

        # Initialize header_type
        header_type = None
        time.sleep(2)
        # Check for 'control id' header
        try:
            if driver.find_element(By.XPATH, "//th[contains(@class, 'cdk-column-id') and contains(text(), 'control id')]"):
                header_type = 'control id'
                print("found control id")
        except NoSuchElementException:
            print("'Control ID' header not found")

        # Check for 'cve id' header
        try:
            if not header_type and driver.find_element(By.XPATH, "//th[contains(@class, 'cdk-column-name') and contains(text(), 'cve id')]"):
                header_type = 'cve id'
                print("found cve id")
        except NoSuchElementException:
            print("'CVE ID' header not found")

        if header_type is None:
            print("Neither 'control id' nor 'cve id' header is found for the description element")

        # Verify the number of rows in tbody based on the header type
        rows = driver.find_elements(By.CSS_SELECTOR, "tbody[role='rowgroup'] > tr")
        if header_type == 'control id' and len(rows) != 1:
            print("Expected 2 row for 'control id', found " + str(len(rows)))
        elif header_type == 'cve id' and len(rows) != 3:
            print("Expected 3 rows for 'cve id', found " + str(len(rows)))
        elif header_type:
            print("Verification successful with header type: " + header_type + " and number of rows: " + str(len(rows)))
        else:
            print("Header type not identified")

    except StaleElementReferenceException:
        print("Encountered a stale element reference. Re-trying to find and click the element.")
        # Optionally, retry locating and clicking the element

    except Exception as e:
        print(f"An error occurred: {e}")


def create_attack_path(manifest_filename='./manifest.yaml'):
    
    # Get the current directory
    current_directory = os.path.dirname(os.path.realpath(__file__))

    # Path to the manifest.yaml file
    manifest_path = os.path.join(current_directory, manifest_filename)

    # Command to execute
    command = f"kubectl apply -f {manifest_path}"

    # Execute the command
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Command output:", result.stdout.decode())
    except subprocess.CalledProcessError as e:
        print("Error occurred:", e.stderr.decode())

def navigate_to_attack_path(wait):
    try:
        # Wait until the element is clickable
        attack_path_element = wait.until(EC.element_to_be_clickable((By.ID, "attack-path-left-menu-item")))
        attack_path_element.click()
        print("Attack-path clicked.")
    except Exception as e:
        print(f"Attach path not found. Error: {e}")
    

def attach_path(driver, wait):
    # go to attcat path gage
    try:
        attack_path_element = wait.until(EC.element_to_be_clickable((By.ID, "attack-path-left-menu-item")))
        attack_path_element.click()
        print("Attach-path clicked.")
    except :
        print("Attach path not found.")    

# click on scane button
    # try:
    #     scan_all_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'armo-button') and contains(@class, 'primary') and contains(@class, 'xl') and contains(text(), 'Scan all')]")))
    #     scan_all_button.click()
    #     print("Scan all button clicked.")
    # except :
    #     print("Scan all button not found.")
    #     driver.save_screenshot(f"./failed_to_find_the_scan_all_button_{ClusterManager.get_current_timestamp()}.png")

    # Check if the Attack path is displayed    
    try:
        data_test_id = "attack-chains-list"
        wait = WebDriverWait(driver, 300, 0.001) # 5 minutes timeout
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, f"[data-test-id='{data_test_id}']")))
        print("Attack path is displayed.")


        # Obtain descriptions
        descriptions = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-test-id='description']")))

        if len(descriptions) < 2:
            print("Expected 2 elements with 'data-test-id=description', found " + str(len(descriptions)))
            exit(1)
        else:
            print("found " + str(len(descriptions)) + " elements with data-test-id=description")
            
            # Verify and click first description
            verify_and_click_description(0,wait, driver)

            try:
                link = driver.find_element(By.XPATH, "/html/body/armo-root/div/div/div/armo-attack-chain-details-page/div[1]/armo-attack-chain-details-breadcrumb-container/armo-breadcrumbs/ul/li[1]/a/armo-button/button")
                link.click()
                print("Clicked on 'Attack Path' link.")
            except NoSuchElementException:
                print("Link not found.")
            time.sleep(1)
            # Verify and click second description
            verify_and_click_description(1,wait, driver)

    except NoSuchElementException:
        print("Attack path is NOT displayed.")
        driver.save_screenshot(f"./failed_to_find_the_attack_path_{ClusterManager.get_current_timestamp()}.png")



def perform_cleanup(driver):
    print("Performing cleanup")
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
    email_user_flow = os.environ.get('email_user_flow')
    login_pass_user_flow = os.environ.get('login_pass_user_flow')
    prod_url = "https://cloud.armosec.io/compliance"
    url = sys.argv[1] if len(sys.argv) > 1 else prod_url

    # Setup the driver
    driver = initialize_driver()
    wait = WebDriverWait(driver, 60, 0.001)

    try:
        # Login
        start_time = time.time()
        cluster_manager = ClusterManager(driver)
        cluster_manager.login(email_user_flow, login_pass_user_flow, url)
        login_time = time.time() - start_time

        create_attack_path(manifest_filename='manifest.yaml')
        
        # Connecting the cluster
        connect_cluster = ConnectCluster(driver)
        connect_cluster.click_get_started()
        connect_cluster.connect_cluster_helm()
        connect_cluster.verify_installation()
        connect_cluster.view_cluster_button()
        connect_cluster.view_connected_cluster()
        onboarding_time = time.time() - start_time

        # attack patč
        # navigate_to_attack_path(wait)
        # time.sleep(5)

        # Navigating to dashboard
        comp_start_time = time.time()
        resource_name = navigate_to_dashboard(driver,wait)
        complince_time = time.time() - comp_start_time

        # Navigating to vulnerabilities 
        vul_start_time = time.time()
        container_name = navigate_to_vulnerabilities(driver, wait)
        vulnerabilities_time = time.time() - vul_start_time
        risk_acceptance_page(driver, wait)
        ac_start_time = time.time() 
        attach_path(driver, wait) 
        ac_time = time.time() - ac_start_time
        np_stat_time = time.time()
        navigate_to_network_policy(driver, wait)
        np_time =  time.time() - np_stat_time - 120 # 2 min waiting time
        # np_time = 0 # NP test desabled
        np_time =  time.time() - np_stat_time
        
        
        log_data = {
            'timestamp': ClusterManager.get_current_timestamp("special"),
            'login_time': f"{login_time:.2f}",
            'onboarding_time': f"{onboarding_time:.2f}",
            'onboarding_time_excluding_login': f"{(onboarding_time - login_time):.2f}",
            'compliance_time': f"{complince_time:.2f}",
            'vulnerabilities_time': f"{vulnerabilities_time:.2f}",
            'NP_time': f"{np_time:.2f}",
            'AC_time': f"{ac_time:.2f}"
        }   
        print(f"Timestamp: {log_data['timestamp']}\n"
            f"Login Time: {log_data['login_time']} sec\n"
            f"Onboarding Time: {log_data['onboarding_time']} sec\n"
            f"Onboarding Time (Excluding Login): {log_data['onboarding_time_excluding_login']} sec\n"
            f"Compliance Time: {log_data['compliance_time']} sec\n"
            f"Vulnerabilities Time: {log_data['vulnerabilities_time']} sec\n"
            f"Network Policy Time: {log_data['NP_time']} sec\n"
            f"Attack Path Time: {log_data['AC_time']} sec")


        with open("./logs/flow_user_logs.csv", "a") as f:
            f.write(','.join(str(log_data[key]) for key in log_data) + '\n')  
            
    finally:
        # Cleanup cluster from Armo platrom
        perform_cleanup(driver)
        driver.quit()        


if __name__ == "__main__":
     main()       