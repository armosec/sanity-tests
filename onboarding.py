import os
import subprocess
import time
import datetime
import logging
from dataclasses import dataclass
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from interaction_manager import InteractionManager, InteractionManagerConfig

ARMO_PLATFORM_URL = "https://cloud.armosec.io/compliance"

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


@dataclass
class OnboardingDetails:
    onboarding_time: float
    onboarding_time_without_login: float

    def to_file(self, file_path: str) -> None:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(file_path, "a") as f:
            f.write(
                f"{timestamp},{self.onboarding_time},{self.onboarding_time_without_login}\n")

    def __str__(self) -> str:
        return f"Onboarding time: {self.onboarding_time}, Onboarding time without login: {self.onboarding_time_without_login}"

    def __repr__(self) -> str:
        return self.__str__()


class OnboardingTest:
    def __init__(self) -> None:
        _config = InteractionManagerConfig.from_env()
        self._interaction_manager = InteractionManager(_config)

    @staticmethod
    def _get_current_timestamp() -> str:
        return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    def _login(self) -> None:
        _logger.info("Logging in to Armo")
        self._interaction_manager.navigate(ARMO_PLATFORM_URL)
        mail_input = self._interaction_manager.wait_until_interactable(
            '//*[@id="frontegg-login-box-container-default"]/div[1]/input'
        )
        mail_input.send_keys(os.environ['email_onboarding'])
        mail_input.send_keys(Keys.ENTER)
        password_input = self._interaction_manager.wait_until_interactable(
            '/html/body/frontegg-app/div[2]/div[2]/input'
        )
        password_input.send_keys(os.environ['login_pass_onboarding'])
        password_input.send_keys(Keys.ENTER)

    def _click_get_started(self) -> None:
        try:
            _logger.info("Clicking on get started button")
            self._interaction_manager.click('//*[@id="action-section"]/armo-button/button')
            _logger.info("Clicked on get started button")
        except TimeoutException as e:
            _logger.error("Get started button was not found or clickable.",
                          exc_info=True, stack_info=True, extra={'screenshot': True})
            self._interaction_manager.driver.save_screenshot(
                f"./get_started_button_error_{self._get_current_timestamp()}.png")
            raise e

    def _copy_helm_command(self) -> str:
        _logger.info("Copying helm command")
        helm_command_element = self._interaction_manager.wait_until_interactable(
            "//div[@class='command-area']//span[@class='ng-star-inserted']"
        )
        helm_command = helm_command_element.text
        _logger.info("Copied helm command")
        return helm_command

    def _execute_helm_command(self, helm_command: str) -> None:
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
        _logger.info("Verifying installation")
        try:
            self._interaction_manager.click(
                "//div[@id='cdk-overlay-0']//armo-dialog-footer//button[contains(@class, 'armo-button') and contains(text(), 'Verify installation')]"
            )
        except TimeoutException as e:
            _logger.error("Verify button was not found or clickable.",
                          exc_info=True, stack_info=True, extra={'screenshot': True})
            self._interaction_manager.driver.save_screenshot(
                f"./verify_button_error_{self._get_current_timestamp()}.png")
            raise e
        _logger.info("Verified installation")

    def _view_cluster_button(self) -> None:
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
            '//*[@id="settings-left-menu-item"]'
        )
        _logger.info("Clicked on settings button")

    def _click_more_options_button(self) -> None:
        _logger.info("Clicking on more options button")
        self._interaction_manager.click(
            '/html/body/armo-root/div/div/div/div/armo-clusters-page/armo-clusters-table/div/table/tbody/tr/td[9]/armo-row-options-button/armo-icon-button/armo-button/button'
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
        self._uninstall_kubescape()
        self._click_settings_button()
        self._click_more_options_button()
        self._choose_delete_option()
        self._confirm_delete()
        self._wait_for_empty_table()
        _logger.info("Performed cleanup")

    def run(self) -> None:
        start_time = time.time()
        self._login()
        login_time = time.time()
        self._click_get_started()
        helm_command = self._copy_helm_command()
        self._execute_helm_command(helm_command)
        self._verify_installation()
        self._view_cluster_button()
        self._view_connected_cluster()
        end_time = time.time()
        self._perform_cleanup()
        self._interaction_manager.quit()

        onboarding_time = "{:.2f}".format(end_time - start_time)
        lonboarding_time_without_login = "{:.2f}".format(end_time - login_time)
        onboarding_details = OnboardingDetails(
            onboarding_time, lonboarding_time_without_login)
        onboarding_details.to_file("./logs/onboarding_logs.csv")
        _logger.info(f"Onboarding details: {onboarding_details}")

if __name__ == "__main__":
    OnboardingTest().run()
