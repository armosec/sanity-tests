import os
import subprocess
import logging
from .base_test import BaseTest

logger = logging.getLogger(__name__)

class AttackSuiteScenarios(BaseTest):
    
    SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "scripts")
    
    def __init__(self, driver, wait):
        self._driver = driver
        self._wait = wait
        
    def run(self):
        logger.info("No script specified to run. Please call run_script('script-name.sh') manually if running directly.")
    
    def create_incident(self, script_name):
        script_path = os.path.join(self.SCRIPT_DIR, script_name)
        if not os.path.isfile(script_path):
            logger.error(f"Script not found: {script_path}")
            return False

        logger.info(f"Running script: {script_path}")
        try:
            result = subprocess.run(["bash", script_path], capture_output=True, text=True, check=True)
            logger.info(f"Script output:\n{result.stdout}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Script failed with error:\n{e.stderr}")
            return False
