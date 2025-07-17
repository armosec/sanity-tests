import time
import logging
from ...base_test import BaseTest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from ...cluster_operator import ClusterManager

logger = logging.getLogger(__name__)

class AgentAccessKeys(BaseTest):    
    def run(self):
        logger.info("Starting Agent Access Keys test")
        self.run_test()

    def run_test(self):
        driver = self._driver
        interaction_manager = self._interaction_manager
        cluster_manager = ClusterManager(self._driver, self._wait)
        try:
            interaction_manager.click('agent-access-tokens-settings-left-menu-item', By.ID)
            logger.info("Agent Access Keys clicked")
        except:
            logger.error("Failed to click on Agent Access Keys")
            driver.save_screenshot(f"./failed_to_click_on_agent_access_keys_{ClusterManager.get_current_timestamp()}.png")
