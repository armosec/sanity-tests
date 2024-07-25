# main.py
import os
import sys
from selenium.webdriver.support.ui import WebDriverWait
from tests.selenium_config import initialize_driver
from tests.interaction_manager import InteractionManager
from tests.vulnerabilities import Vulnerabilities
from tests.compliance import Compliance
from tests.base_test import TestConfig
from concurrent.futures import ThreadPoolExecutor, as_completed

class TestsRunner:
    def __init__(self, tests_with_credentials_and_env):
        self.tests_with_credentials_and_env = tests_with_credentials_and_env

    def run(self):
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.run_test, test_class, email, password, environment) 
                       for test_class, email, password, environment in self.tests_with_credentials_and_env]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as exc:
                    print(f"Test generated an exception: {exc}")

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
    if len(sys.argv) < 5 or (len(sys.argv) - 2) % 3 != 0:
        print("Usage: python main.py [ENVIRONMENT] [test_name1 email1 password1 ... test_nameN emailN passwordN]")
        sys.exit(1)

    environment = sys.argv[1]
    test_names_and_credentials = sys.argv[2:]

    test_mapping = {
        'vulnerabilities': Vulnerabilities,
        'compliance': Compliance,
        # Add additional mappings here
    }

    tests_with_credentials_and_env = []
    for i in range(0, len(test_names_and_credentials), 3):
        test_name = test_names_and_credentials[i]
        email = test_names_and_credentials[i+1]
        password = test_names_and_credentials[i+2]

        test_class = test_mapping.get(test_name.lower())
        if not test_class:
            print(f"Unknown test: {test_name}")
            sys.exit(1)

        tests_with_credentials_and_env.append((test_class, email, password, environment))

    test_runner = TestsRunner(tests_with_credentials_and_env)
    test_runner.run()

if __name__ == "__main__":
    main()
