import time
import logging
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException

# Set up logging
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

class LoginManager:
    """
    A reusable class to handle login functionality for Armo platform tests.
    Can be used across different test modules (userFlow, latency, etc.)
    """
    
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait
    
    def wait_for_page_load(self, timeout=20):
        """Wait for the page to fully load"""
        WebDriverWait(self.driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
    
    def get_shadow_root(self, max_retries=5):
        """Fetch the shadow root dynamically with retries to avoid stale references."""
        for attempt in range(max_retries):
            try:
                _logger.info(f"Attempt {attempt+1}: Getting shadow root")
                
                # Ensure the page is fully loaded
                self.wait_for_page_load()
                
                # Explicitly wait for the shadow host element to appear
                shadow_host = WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.ID, "frontegg-login-box-container-default"))
                )
                
                # Check if the element is still attached
                if not self.driver.execute_script("return document.contains(arguments[0]);", shadow_host):
                    _logger.warning(f"Attempt {attempt+1}: Shadow host is no longer attached to DOM. Retrying...")
                    time.sleep(2)
                    continue
                
                # Ensure shadow root exists before returning it
                shadow_root = self.driver.execute_script("return arguments[0].shadowRoot", shadow_host)
                
                if shadow_root:
                    _logger.info("Successfully retrieved shadow root!")
                    return shadow_root
                
                _logger.warning("Shadow root is not yet available, retrying...")
                
            except (StaleElementReferenceException, TimeoutException) as e:
                _logger.warning(f"Retrying shadow root fetch... Attempt {attempt + 1}/{max_retries}: {str(e)}")
                time.sleep(2)
            
        self.driver.save_screenshot("shadow_root_error.png")
        raise RuntimeError("Failed to get shadow root after multiple attempts")

    def login(self, email, password, url="https://cloud.armosec.io"):
        """
        Handles logging into the Armo platform using shadow DOM elements.
        
        Args:
            email (str): Email address for login
            password (str): Password for login
            url (str): The URL to navigate to for login
        
        Returns:
            float: Time taken for login in seconds
        """
        _logger.info(f"Logging in to Armo at {url}")
        start_time = time.time()
        
        self.driver.get(url)
        self.wait_for_page_load()

        # Clear cookies and storage to avoid stale sessions
        try:
            self.driver.delete_all_cookies()
            self.driver.execute_script("window.localStorage.clear();")
            self.driver.execute_script("window.sessionStorage.clear();")
        except Exception as e:
            _logger.warning(f"Failed to clear storage: {e}")

        time.sleep(3)  # Ensure JavaScript elements are fully initialized

        try:
            shadow_root = self.get_shadow_root()

            email_input = WebDriverWait(self.driver, 20).until(
                lambda d: shadow_root.find_element(By.CSS_SELECTOR, "input[name='identifier']")
            )
            email_input.clear()
            email_input.send_keys(email)
            email_input.send_keys(Keys.ENTER)

            time.sleep(2)
            shadow_root = self.get_shadow_root()

            password_input = WebDriverWait(self.driver, 20).until(
                lambda d: shadow_root.find_element(By.CSS_SELECTOR, "input[name='password']")
            )
            password_input.clear()
            password_input.send_keys(password)
            password_input.send_keys(Keys.ENTER)

            WebDriverWait(self.driver, 30).until(
                lambda d: "login" not in d.current_url.lower()
            )

            _logger.info("Login successful!")
            
            login_time = time.time() - start_time
            _logger.info(f"Login completed in {login_time:.2f} seconds")
            return login_time

        except TimeoutException:
            self.driver.save_screenshot("login_timeout_error.png")
            raise Exception("Login failed due to timeout.")

        except Exception as e:
            self.driver.save_screenshot("login_error.png")
            
            # If login fails, attempt a page refresh and retry login once
            _logger.warning(f"Login attempt failed: {str(e)}. Retrying after page refresh.")
            self.driver.refresh()
            time.sleep(5)
            
            try:
                return self.login(email, password, url)  # Retry login once
            except Exception as retry_error:
                raise Exception(f"Login failed after retry: {str(retry_error)}")