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
from tests.base_test import TestConfig
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

class TestsRunner:
    def __init__(self, tests_with_credentials):
        self.tests_with_credentials = tests_with_credentials

    def run(self):
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.run_test, test_class, email, password, environment) 
                       for test_class, email, password, environment in self.tests_with_credentials]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as exc:
                    _logger.error(f"Test generated an exception: {exc}")

    def run_test(self, test_class, email, password, environment):
        driver = initialize_driver()
        interaction_manager = InteractionManager(driver)
        test_config = TestConfig(
            driver=driver,
            interaction_manager=interaction_manager,
            email=email,
            password=password,
            environment=environment
        )
        test_instance = test_class(test_config)
        try:
            test_instance.run()
        finally:
            driver.quit()

def main():
    if len(sys.argv) < 4 or (len(sys.argv) - 1) % 4 != 0:
        print("Usage: python main.py [environment test_name email password ...]")
        sys.exit(1)

    test_data = sys.argv[1:]

    test_mapping = {
        'vulnerabilities': Vulnerabilities,
        'compliance': Compliance,
        'attach_path': AttachPath,
        # Add additional mappings here
    }

    tests_with_credentials = []
    for i in range(0, len(test_data), 4):
        environment = test_data[i]
        test_name = test_data[i+1]
        email = test_data[i+2]
        password = test_data[i+3]

        test_class = test_mapping.get(test_name.lower())
        if not test_class:
            print(f"Unknown test: {test_name}")
            sys.exit(1)

        tests_with_credentials.append((test_class, email, password, environment))

    test_runner = TestsRunner(tests_with_credentials)
    test_runner.run()

if __name__ == "__main__":
    main()
