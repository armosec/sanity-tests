from selenium import webdriver
from dataclasses import dataclass
from abc import ABC, abstractmethod
from selenium.webdriver.common.keys import Keys
from .interaction_manager import InteractionManager
from .cluster_operator import Cleanup, ClusterManager
from selenium.webdriver.support.ui import WebDriverWait

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
        self._driver.get(url)
        email_element = self._interaction_manager.focus_and_send_text('//*[@id="frontegg-login-box-container-default"]/div[1]/input', self._email)
        email_element.send_keys(Keys.ENTER)
        password_element = self._interaction_manager.focus_and_send_text('/html/body/frontegg-app/div[2]/div[2]/input', self._password)
        password_element.send_keys(Keys.ENTER)
        
    def get_login_url(self):
        environment_urls = {
            "development": "https://cloud-predev.armosec.io/",
            "staging": "https://cloud-stage.armosec.io/",
            "production": "https://cloud.armosec.io/"
        }
        return environment_urls.get(self._environment, "https://cloud.armosec.io/")
        

    def perform_cleanup(self):
        cleanup = Cleanup(self._driver)
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
