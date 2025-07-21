import time
import logging

from .agent_access_keys import AgentAccessKeys
from ...base_test import BaseTest
from selenium.webdriver.common.by import By
from ...cluster_operator import ClusterManager, ConnectCluster

logger = logging.getLogger(__name__)

class Settings(BaseTest):
    def run(self):
        connect_cluster = ConnectCluster(self._driver, self._wait)
        cluster_manager = ClusterManager(self._driver, self._wait)
        # cluster_manager.create_attack_path()  
        login_url = self.get_login_url()
        self.login(login_url)
        try:
            interact = self._interaction_manager
            interact.click('settings-left-menu-item', By.ID)  # Click on settings page
            
            # Only perform cluster setup if create_cluster is True
            if self._create_cluster:
                connect_cluster.click_get_started()
                connect_cluster.connect_cluster_helm()
                connect_cluster.verify_installation()
                connect_cluster.view_cluster_button()
                connect_cluster.view_connected_cluster()
                cluster_manager.create_attack_path()
                print("Wait for 30 seconds")
                time.sleep(30)
                
            print("Running settings test")
            
            agent_access_keys = AgentAccessKeys(self.config)
            agent_access_keys.run()
        finally:
            # Only perform cleanup if we created a cluster
            if self._create_cluster:
                self.perform_cleanup()
            logger.info("Settings test completed")
