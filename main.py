# main.py

import os
import sys
import logging
from selenium.webdriver.support.ui import WebDriverWait
from tests.selenium_config import initialize_driver
from tests.interaction_manager import InteractionManager
from tests.vulnerabilities import Vulnerabilities
from tests.compliance import Compliance
from tests.attach_path import AttachPath
from tests.security_risk import SecurityRisk
from tests.runtime_incidents import RuntimeIncident
from tests.base_test import TestConfig
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

class TestsRunner:
    def __init__(self, tests_with_credentials):
        self.tests_with_credentials = tests_with_credentials

    def run(self):
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.run_test, test_class, email, password, environment, create_cluster) 
                    for test_class, email, password, environment, create_cluster in self.tests_with_credentials]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as exc:
                    _logger.error(f"Test generated an exception: {exc}")

    def run_test(self, test_class, email, password, environment, create_cluster):
        driver = initialize_driver()
        interaction_manager = InteractionManager(driver)
        test_config = TestConfig(
            driver=driver,
            interaction_manager=interaction_manager,
            email=email,
            password=password,
            environment=environment,
            create_cluster=create_cluster  # Pass the create_cluster flag
        )
        test_instance = test_class(test_config)
        try:
            test_instance.run()
        finally:
            driver.quit()

def main():
    # Check if we have at least the basic arguments (environment, test_name, email, password)
    if len(sys.argv) < 5:
        print("Usage: python main.py environment test_name email password create_cluster [environment test_name email password create_cluster ...]")
        sys.exit(1)

    test_data = sys.argv[1:]
    
    # Check if we have complete sets of parameters (sets of 5)
    if len(test_data) % 5 != 0:
        print("Error: Incomplete set of arguments. Each test requires 5 arguments: environment, test_name, email, password, create_cluster")
        sys.exit(1)

    test_mapping = {
        'vulnerabilities': Vulnerabilities,
        'compliance': Compliance,
        'attach-path': AttachPath,
        # 'runtime-security': RuntimeIncident,
        'security-risk': SecurityRisk

        # Add additional mappings here
    }

    tests_with_credentials = []
    for i in range(0, len(test_data), 5):
        environment = test_data[i]
        test_name = test_data[i+1]
        email = test_data[i+2]
        password = test_data[i+3]
        create_cluster = test_data[i+4].lower() == 'true'  # Convert string to boolean
        
        test_class = test_mapping.get(test_name.lower())
        if not test_class:
            print(f"Unknown test: {test_name}")
            sys.exit(1)

        tests_with_credentials.append((test_class, email, password, environment, create_cluster))

    test_runner = TestsRunner(tests_with_credentials)
    test_runner.run()

if __name__ == "__main__":
    main()