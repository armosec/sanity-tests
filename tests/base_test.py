from selenium import webdriver
from dataclasses import dataclass
from abc import ABC, abstractmethod
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from .interaction_manager import InteractionManager
from .cluster_operator import Cleanup, ClusterManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .login_manager import LoginManager

@dataclass
class TestConfig:
    driver: webdriver.Chrome
    interaction_manager: InteractionManager
    email: str
    password: str
    environment: str
    
class BaseTest(ABC):
    def __init__(self, config: TestConfig) -> None:
        self._driver = config.driver
        self._interaction_manager = config.interaction_manager
        self._email = config.email
        self._password = config.password
        self._environment = config.environment
        self._wait = WebDriverWait(self._driver, 60, 0.001)
    
    @abstractmethod
    def run(self):
        pass

    def login(self, url: str):
        """
        Log in to the application using the LoginManager
        
        Args:
            url: The URL to navigate to for login
        """
        login_manager = LoginManager(self._driver, self._wait)
        login_manager.login(self._email, self._password, url)
        
        # Check for onboarding if needed
        try:
            onboarding_wait = WebDriverWait(self._driver, 5, 0.001)
            element = onboarding_wait.until(EC.visibility_of_element_located(
                (By.XPATH, "//div[@class='label font-semi-bold font-size-18 my-3' and contains(text(), 'What do you do?')]")
            ))
            print("Onboarding role page is displayed - sign-up user (first login)")
            self._handle_onboarding()
        except:
            print("No onboarding page detected - existing user")
        
    def get_login_url(self):
        environment_urls = {
            "predev": "https://cloud-predev.armosec.io/",
            "dev": "https://cloud-dev.armosec.io/",
            "staging": "https://cloud-stage.armosec.io/",
            "production": "https://cloud.armosec.io/"
        }
        return environment_urls.get(self._environment, "https://cloud.armosec.io/")
        

    def perform_cleanup(self):
        cleanup = Cleanup(self._driver, self._wait)
        try:
            print("Performing cleanup")
            cleanup.uninstall_kubescape()
            cleanup.click_settings_button()   
            cleanup.click_more_options_button()
            cleanup.choose_delete_option()
            cleanup.confirm_delete()
            cleanup.wait_for_empty_table()
            print("Cleanup performed successfully")

        except:
            print("Failed to perform cleanup")
            self._driver.save_screenshot(f"./failed_to_perform_cleanup_{ClusterManager.get_current_timestamp()}.png")
            exit(1)
