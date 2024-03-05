import os
import sys
import subprocess
import time
import datetime
import logging
import json
from dataclasses import dataclass
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from interaction_manager import InteractionManager, InteractionManagerConfig

ARMO_PLATFORM_URL = "https://cloud.armosec.io/dashboard"
ACCOUNT_DATA_JSON_PATH = "./accountsData.json"

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


@dataclass
class PaymentDetails:
    onboarding_time: float
    onboarding_time_without_login: float

    def __str__(self) -> str:
        return f"Onboarding time: {self.onboarding_time}, Onboarding time without login: {self.onboarding_time_without_login}"

    def __repr__(self) -> str:
        return self.__str__()
    


@dataclass
class PaymenyTest:

    actual_results = {
        "dashboard": 0,
        "compliance": 0,
        "A.C_main_page": 0,
        "A.C_details_page": 0,
        "Vuln": 0,
        "NP": 0,
        "RBAC": 0,
        "risk_accept": 0,
        "repo_scan": 0,
        "registry_scan": 0
}

    def __init__(self) -> None:
        _config = InteractionManagerConfig.from_env()
        self._interaction_manager = InteractionManager(_config)
        self.account_data = self.load_json(ACCOUNT_DATA_JSON_PATH)  
        self.access_data = self.account_data['access'] 

    def __repr__(self) -> str:
        return self.__str__()
    
    def load_json(self,filename):
        with open(filename, 'r') as file:
            return json.load(file)

    @staticmethod
    def _get_current_timestamp() -> str:
        return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
        
    def get_account_type(self,env_name ,account_id, account_data):
        for env_name, accounts in account_data['env'].items():
            for account in accounts:
                if account['accountID'] == account_id:
                    return account['type']
        return None


    def _login(self) -> None:
        _logger.info("Logging in to Armo")
        self._interaction_manager.navigate(ARMO_PLATFORM_URL)
        mail_input = self._interaction_manager.wait_until_interactable(
            '//*[@id="frontegg-login-box-container-default"]/div[1]/input'
        )
        mail_input.send_keys(os.environ['email_sso'])
        mail_input.send_keys(Keys.ENTER)
        password_input = self._interaction_manager.wait_until_interactable(
            '/html/body/frontegg-app/div[2]/div[2]/input'
        )
        password_input.send_keys(os.environ['login_pass_sso'])
        password_input.send_keys(Keys.ENTER)

    def _chose_user(self) -> None: 
        _logger.info("Choosing user")
        self._interaction_manager.click(
            '/html/body/armo-root/div/div/armo-header/div/armo-user-extended-menu/div/armo-user-tenants-menu/div/div/span'
        )
    
    def click_on_account_by_id(self, account_id):
        found = False  # Flag to indicate if the account ID was found and clicked
        try:
            # Correcting to use _interaction_manager as defined in the __init__ method
            tenant_list_items = self._interaction_manager.find_elements_by_css_selector("armo-tenants-list-item")
            
            time.sleep(0.5)
            for item in tenant_list_items:
                guid_text_element = item.find_element(By.CSS_SELECTOR, "section[id='guid_section'] p")
                if guid_text_element.text.strip() == account_id.strip():
                    # Clicking the <p> element where the ID is
                    guid_text_element.click()
                    print(f"Clicked on account with ID: {account_id}")
                    found = True
                    break
                
            if not found:
                _logger.error("Account ID not found.")

        except Exception as e:
            _logger.error(f"An error occurred while trying to click on account by ID {account_id}: {e}")

        # refresh the page 
        self._interaction_manager.driver.refresh()
        _logger.info("Page refreshed.")
        return found



    def _click_get_started(self) -> None:
        try:
            _logger.info("Clicking on get started button")
            self._interaction_manager.click(
                '/html/body/armo-root/div/div/div/armo-home-page/armo-home-empty-state/armo-empty-state-page/main/section[1]/div/armo-button/button'
            )
            _logger.info("Clicked on get started button")
        except TimeoutException as e:
            if self.account_type != "blocked":
                _logger.error("Get started button was not found or clickable.",
                              exc_info=True, stack_info=True, extra={'screenshot': True})
                self._interaction_manager.driver.save_screenshot(
                    f"./get_started_button_error_{self._get_current_timestamp()}.png")
                raise e
            else:
                _logger.info("Get started button was not found or clickable. Account is blocked.")

    def _copy_helm_command(self) -> str:
        if self.account_type == "blocked":
            _logger.info("Account is blocked. Skipping helm command.")
            return ""
        _logger.info("Copying helm command")
        helm_command_element = self._interaction_manager.wait_until_interactable(
            "//div[@class='command-area']//span[@class='ng-star-inserted']"
        )
        helm_command = helm_command_element.text
        _logger.info("Copied helm command")
        return helm_command

    def _execute_helm_command(self, helm_command: str) -> None:
        if self.account_type == "blocked":
            _logger.info("Account is blocked. Skipping helm command execution.")
            return
        _logger.info("Executing helm command")
        try:
            _ = subprocess.run(helm_command, shell=True,
                               check=True, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            _logger.error(f"Helm command execution failed with error: {e}")
            if e.stderr:
                _logger.error(e.stderr.decode('utf-8'))
            raise e
        _logger.info("Executed helm command successfully")

    def _verify_installation(self) -> None:
        if self.account_type == "blocked":
            _logger.info("Account is blocked. Skipping installation verification.")
            return
        _logger.info("Verifying installation")
        try:
            self._interaction_manager.click(
                "//armo-dialog-footer//*[contains(@class, 'mat-button-wrapper')]"
            )
        except TimeoutException as e:
            _logger.error("Verify button was not found or clickable.",
                          exc_info=True, stack_info=True, extra={'screenshot': True})
            self._interaction_manager.driver.save_screenshot(
                f"./verify_button_error_{self._get_current_timestamp()}.png")
            raise e
        _logger.info("Verified installation")

    def _view_cluster_button(self) -> None:
        if self.account_type == "blocked":
            _logger.info("Account is blocked. Skipping view cluster button.")
            return
        _logger.info("Clicking on view cluster button")
        try:
            self._interaction_manager._timeout = 90
            self._interaction_manager.click(
                "//armo-connection-wizard-connection-step-footer//*[contains(@class, 'armo-button')]", click_delay=3
            )
            self._interaction_manager._timeout = self._interaction_manager._config.timeout
        except TimeoutException as e:
            _logger.error("View cluster button was not found or clickable.",
                          exc_info=True, stack_info=True, extra={'screenshot': True})
            self._interaction_manager.driver.save_screenshot(
                f"./view_cluster_button_error_{self._get_current_timestamp()}.png")
            raise e
        _logger.info("Clicked on view cluster button")

    def _view_connected_cluster(self) -> None:
        if self.account_type == "blocked":
            _logger.info("Account is blocked. Skipping view connected cluster.")
            return
        _logger.info("Verifying connected cluster")
        try:
            self._interaction_manager.wait_until_interactable(
                "//armo-cluster-scans-table//*[contains(@class, 'mat-tooltip-trigger')]"
            )
        except TimeoutException as e:
            try:
                self._interaction_manager.driver.refresh()
                self._interaction_manager.wait_until_interactable(
                    "//armo-cluster-scans-table//*[contains(@class, 'mat-tooltip-trigger')]"
                )
            except TimeoutException as ex:
                _logger.error("View cluster connected was not found.",
                              exc_info=True, stack_info=True, extra={'screenshot': True})
                self._interaction_manager.driver.save_screenshot(
                    f"./view_connected_cluster_error_{self._get_current_timestamp()}.png")
                raise ex
        _logger.info("Verified connected cluster")

    def create_attack_path(self, manifest_filename='./manifest.yaml')  -> None:
        """
        Apply a Kubernetes manifest file to create an attack path.

        :param manifest_filename: Name of the manifest file, defaults to 'manifest.yaml'
        :return: None
        """
        # Get the current directory
        current_directory = os.path.dirname(os.path.realpath(__file__))

        # Path to the manifest.yaml file
        manifest_path = os.path.join(current_directory, manifest_filename)

        command = f"kubectl apply -f {manifest_path}"
        try:
            result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            _logger.info("Command output: %s", result.stdout.decode())
        except subprocess.CalledProcessError as e:
            _logger.error("Error occurred:", e.stderr.decode())

    def _navigate_to_attack_path(self) -> None:
        _logger.info("Navigating to attack path")   
        try:
            self._interaction_manager.click('//*[@id="attack-path-left-menu-item"]')
        except:
            self.actual_results["A.C_main_page"] = 0
            _logger.info("Can not access to the attack path page", exc_info=True)  
        try:
            _logger.info("Clicking on the fix button of the attack path.")
            self._interaction_manager.click('/html/body/armo-root/div/div/div/armo-attack-chains-page/armo-attack-chains-list/div[1]/armo-attack-chain-item/div[3]/armo-fix-button/armo-button/button')
            self.actual_results["A.C_main_page"] = 1
        except:
            _logger.error("Failed to click on fix button of the attack path", exc_info=True)
            self.actual_results["A.C_main_page"] = 0
        try:
            _logger.info("Navigate to details page of the attach path.")
            self._interaction_manager._timeout = 5
            if self._interaction_manager.element_exists('/html/body/armo-root/div/div/div/armo-attack-chain-details-page/div[2]/div/div[1]/armo-how-to-fix-button/armo-button/button'):
                self.actual_results["A.C_details_page"] = 1
            else:
                self.actual_results["A.C_details_page"] = 0
                _logger.info("Can not get the details page of the attach path")
        except: 
            _logger.error("Unexpected error occurred when trying to navigate to vulnerabilities.", exc_info=True)
        print(self.actual_results)

    def _navigate_to_compliance(self) -> None:
        _logger.info("Navigating to compliance")
        self._interaction_manager.click('//*[@id="configuration-scanning-left-menu-item"]')
        try:
            _logger.info("select cluster")
            self._interaction_manager.click("//armo-cluster-scans-table//*[contains(@class, 'mat-tooltip-trigger')]") 
            # # click on the first control
            self._interaction_manager.click('//*[@id="framework-control-table-remediation-0"]')  
            _logger.info("clicked on the first control")
            self.actual_results["compliance"] = 1
        except:
            _logger.info("Failed to click on the first control in compliance page. Checking for must-upgrade page.")
            # Check if the trial expired page is present
            if self._interaction_manager.element_exists('/html/body/armo-root/div/div/div/armo-must-upgrade-page/armo-button/button'):
                _logger.info("Must upgrade page is present.")
                self.actual_results["compliance"] = 0
            else:
                _logger.error("Unexpected error occurred when trying to navigate to complaince", exc_info=True)
        print(self.actual_results)


    def _navigate_to_dashboard(self) -> bool:
        _logger.info("Navigating to dashboard")
        try:
            self._interaction_manager.click('//*[@id="dashboard-left-menu-item"]')
            _logger.info("Clicked on dashboard")
        except:
            if self._interaction_manager.element_exists('/html/body/armo-root/div/div/div/armo-must-upgrade-page/armo-button/button') and self.account_type == "blocked":
                _logger.error("Account blocked. Must upgrade page is present.", exc_info=True)  
                self.actual_results["dashboard"] = 0
                return True
            else:
                _logger.error("Unexpected error occurred when trying to navigate to dashboard.",
                              exc_info=True, stack_info=True, extra={'screenshot': True})
                self._interaction_manager.driver.save_screenshot(
                f"./navigate_to_dashboard_error_{self._get_current_timestamp()}.png") 
                return False
                 
        try:
            # Wait for the element to exist
            cluster_count_element = self._interaction_manager.wait_until_css_exists('span.cluster-acronym.font-semi-bold.mr-2')
            cluster_count = cluster_count_element.text.strip()
            if cluster_count == "1":
                _logger.info("Verification successful: There is 1 cluster.")
                self.actual_results["dashboard"] = 1
            else:
                _logger.info(f"Verification failed: Expected 1 cluster, found {cluster_count}.")
                self.actual_results["dashboard"] = 0
        except TimeoutException:
            _logger.error("The cluster count element does not exist on the page.",
                          exc_info=True, stack_info=True, extra={'screenshot': True})
            self._interaction_manager.driver.save_screenshot(
                f"./cluster_count_element_does_not_exist_{self._get_current_timestamp()}.png")
            return False
        
    def _navigate_to_vulnerabilities(self) -> None:
        _logger.info("Navigating to vulnerabilities")
        self._interaction_manager._timeout = 5
        try:
            self._interaction_manager.click('//*[@id="image-scanning-left-menu-item"]')
        except:
            if self._interaction_manager.element_exists('/html/body/armo-root/div/div/div/armo-must-upgrade-page/armo-button/button') and self.account_type == "blocked":
                _logger.error("Account blocked. Must upgrade page is present.", exc_info=True)  
                self.actual_results["Vuln"] = 0       
        try:
            # Attempt to click on the first workload
            self._interaction_manager.click('/html/body/armo-root/div/div/div/armo-workloads-page/armo-vulnerabilities-shared-table/div/table/tbody/tr[1]/td[2]')
            _logger.info("Successfully clicked on the first workload.")
            self.actual_results["Vuln"] = 1
        except Exception as e:
            _logger.info("Failed to click on the first workload. Checking for trial expired page.")
            # Check if the trial expired page is present
            if self._interaction_manager.element_exists('/html/body/armo-root/div/div/div/armo-trial-expired-page/armo-button/button'):
                _logger.info("Trial expired page is present.")
                self.actual_results["Vuln"] = 0
            else:
                _logger.error("Unexpected error occurred when trying to navigate to vulnerabilities.", exc_info=True)
        print(self.actual_results)

    def _navigate_to_RBAC(self) -> None:
        _logger.info("Navigating to RBAC")
        self._interaction_manager._timeout = 5
        try:
            self._interaction_manager.click('//*[@id="rbac-visualizer-left-menu-item"]')
        except:
            if self._interaction_manager.element_exists('/html/body/armo-root/div/div/div/armo-must-upgrade-page/armo-button/button') and self.account_type == "blocked":
                _logger.error("Account blocked. Must upgrade page is present.", exc_info=True)  
                self.actual_results["RBAC"] = 0
                return True
        try:
            # Wait for the element to exist
            self._interaction_manager.click('/html/body/armo-root/div/div/div/armo-visualizer-page/app-graph/div/div[1]/span/button')
            _logger.info("Clicked on the 'Clraer' button on RBAC page.")
            self.actual_results["RBAC"] = 1
        except:
            _logger.info("Failed to click on the 'Clear' button on RBAC page, Checking upgrade page")
            # Check if the trial expired page is present
            if self._interaction_manager.element_exists('/html/body/armo-root/div/div/div/armo-trial-expired-page/armo-button/button'):
                _logger.info(" Upgrade page is present.")
                self.actual_results["RBAC"] = 0
            else:
                _logger.error("Unexpected error occurred when trying to navigate to RBAC.", exc_info=True)
        print(self.actual_results)
        
    def _navigate_to_page(self, menu_item_xpath: str, page_indicator_xpath: str, page_name: str, json_status: str) -> bool:
        _logger.info(f"Navigating to {page_name}")
        self._interaction_manager._timeout = 5
        self._interaction_manager.click(menu_item_xpath)

        if self._interaction_manager.element_exists(page_indicator_xpath):
            _logger.info(f"{page_name} page is present.")
            self.actual_results[json_status] = 1
        elif self._interaction_manager.element_exists('/html/body/armo-root/div/div/div/armo-trial-expired-page/armo-button/button'):
            _logger.info("Trial expired page is present.")
            self.actual_results[json_status] = 0
        elif self._interaction_manager.element_exists('/html/body/armo-root/div/div/div/armo-must-upgrade-page/armo-button/button'):
            _logger.info("Must upgrade page is present. Blocked account.")
            self.actual_results[json_status] = 0
        else:
            _logger.error(f"Unexpected error occurred when trying to navigate to {page_name}.", exc_info=True)
        print(self.actual_results)
        

    def _navigate_to_risk_acceptance(self) -> None:
        return self._navigate_to_page('//*[@id="rick-acceptance-left-menu-item"]', '//*[@id="mat-tab-link-0"]', "Risk acceptance", "risk_accept")

    def _navigate_to_repo_scanning(self) -> None:
        return self._navigate_to_page('//*[@id="repositories-scan-left-menu-item"]', '//*[@id="action-section"]/armo-button', "Repo scanning", "repo_scan")
    
    def _navigate_to_registry_scanning(self) -> None:
        return self._navigate_to_page('//*[@id="registry-scanning-left-menu-item"]', '//*[@id="action-section"]/armo-button', "Registry scanning", "registry_scan")

    def _uninstall_kubescape(self) -> None:
        _logger.info("Uninstalling kubescape")
        command = "helm uninstall kubescape -n kubescape && kubectl delete ns kubescape"
        process = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            _logger.error(f"Error executing command: {stderr.decode()}")
        else:
            _logger.info(f"Command executed successfully: {stdout.decode()}")
        _logger.info("Uninstalled kubescape")

    def _click_settings_button(self) -> None:
        _logger.info("Clicking on settings button")
        self._interaction_manager.click(
            '/html/body/armo-root/div/armo-side-nav-menu/nav/div[2]/armo-nav-items-list/ul[3]/li'
        )
        _logger.info("Clicked on settings button")

    def _click_more_options_button(self) -> None:
        _logger.info("Clicking on more options button")
        self._interaction_manager.click(
            '/html/body/armo-root/div/div/div/div[2]/armo-clusters-page/armo-clusters-table/div/table/tbody/tr/td[9]/armo-row-options-button/armo-icon-button/armo-button/button/armo-icon'
        )
        _logger.info("Clicked on more options button")

    def _choose_delete_option(self) -> None:
        _logger.info("Choosing delete option")
        self._interaction_manager.click("//button[text()='Delete']")
        _logger.info("Chose delete option")

    def _confirm_delete(self) -> None:
        _logger.info("Confirming delete")
        self._interaction_manager.click(
            "//button[@class='mat-focus-indicator base-button big-button font-bold ml-auto mat-stroked-button mat-button-base mat-warn ng-star-inserted' and @color='warn']"
        )
        _logger.info("Confirmed delete")

    def _wait_for_empty_table(self) -> None:
        _logger.info("Waiting for empty table")
        self._interaction_manager._timeout = 180
        self._interaction_manager.wait_until_interactable(
            "//td[@class='mat-cell text-center ng-star-inserted'][contains(text(), 'No data to display')]"
        )
        self._interaction_manager._timeout = self._interaction_manager._config.timeout
        _logger.info("Waited for empty table")

    def _perform_cleanup(self) -> None:
        _logger.info("Performing cleanup")
        if self.account_type == "blocked":
            _logger.info("Account is blocked. Skipping cleanup.")
            return
        self._uninstall_kubescape()
        self._click_settings_button()
        self._click_more_options_button()
        self._choose_delete_option()
        self._confirm_delete()
        self._wait_for_empty_table()
        _logger.info("Performed cleanup")

    def compare_results(self):
        if not hasattr(self, 'access_data') or not hasattr(self, 'account_type'):
            _logger.error('Access data or account type not set.')
            return

        expected_results = self.access_data.get(self.account_type)

        if expected_results is None:
            _logger.error(f'No access data available for account type: {self.account_type}')
            return

        # Compare actual results with expected results
        for page, expected_access in expected_results.items():
            actual_access = self.actual_results.get(page)
            if actual_access == expected_access:
                _logger.info(f"{page}: PASS (Expected: {expected_access}, Actual: {actual_access})")
            else:
                _logger.error(f"{page}: FAIL (Expected: {expected_access}, Actual: {actual_access})")



    def run(self) -> None:
        account_data = self.load_json(ACCOUNT_DATA_JSON_PATH)
        if len(sys.argv) < 3:
            print("needed: <env> <accountID>")
            sys.exit(1)

        env_name = sys.argv[1]
        account_id = sys.argv[2]

        self.account_type = self.get_account_type(env_name ,account_id, account_data)
        if self.account_type is not None:
            print(f"Account type for ID {account_id}: {self.account_type}")
        else:
            print(f"Account ID {account_id} not found.")
        self._login()
        self._chose_user()
        self.click_on_account_by_id(account_id)
        self._click_get_started()
        helm_command = self._copy_helm_command()
        self._execute_helm_command(helm_command)
        self._verify_installation()
        self._view_cluster_button()
        self._view_connected_cluster()
        self.create_attack_path()
        self._navigate_to_compliance()
        self._navigate_to_dashboard()
        self._navigate_to_vulnerabilities()
        self._navigate_to_RBAC()
        self._navigate_to_risk_acceptance()
        self._navigate_to_repo_scanning()  
        self._navigate_to_registry_scanning()
        self._navigate_to_attack_path()
        self._perform_cleanup()
        self.compare_results()
        self._interaction_manager.quit()

if __name__ == "__main__":
    PaymenyTest().run()
