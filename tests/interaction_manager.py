import logging
import time
from time import sleep
from typing import Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException

_logger = logging.getLogger(__name__)

class InteractionManager:
    def __init__(self, driver: webdriver.Chrome, timeout: int = 60):
        self._driver = driver
        self._timeout = timeout

    def wait_until_interactable(self, xpath: str, by=By.XPATH) -> WebElement:
        element = WebDriverWait(self._driver, self._timeout).until(
            EC.element_to_be_clickable((by, xpath))
        )
        WebDriverWait(self._driver, self._timeout).until(
            EC.visibility_of_element_located((by, xpath))
        )
        scroll_to_element = """
        const element = arguments[0]
        function scrollToElement(element) {
            const elementRect = element.getBoundingClientRect();
            const windowWidth = window.innerWidth || document.documentElement.clientWidth;
            const windowHeight = window.innerHeight || document.documentElement.clientHeight;
            const scrollXTo = Math.max(elementRect.x - ((windowWidth - elementRect.width) / 2) + window.pageXOffset, 0);
            const scrollYTo = Math.max(elementRect.y - ((windowHeight - elementRect.height) / 2) + window.pageYOffset, 0);
            window.scroll({
                left: scrollXTo,
                top: scrollYTo,
                behavior: 'auto'
            });
        }
        scrollToElement(element);
        """
        self._driver.execute_script(scroll_to_element, element)
        self._driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        WebDriverWait(self._driver, self._timeout).until(
            lambda driver: driver.execute_script(
                "return arguments[0].getBoundingClientRect().height > 0 && arguments[0].getBoundingClientRect().bottom <= window.innerHeight;",
                element,
            )
        )
        return element

    def wait_until_exists(self, xpath: str, by=By.XPATH, timeout: Optional[int] = None):
        if not timeout:
            timeout = self._timeout
        element = WebDriverWait(self._driver, timeout).until(
            EC.presence_of_element_located((by, xpath))
        )
        return element

    def click(self, xpath: str, by=By.XPATH, click_delay: Optional[float] = None, index: int = 0, max_retries: int = 3) -> WebElement:
            _logger.info(f'Clicking "{xpath}" at index {index}')
        
            for retry in range(max_retries):
                try:
                    # Find all elements that match the locator
                    elements = WebDriverWait(self._driver, self._timeout).until(
                        EC.presence_of_all_elements_located((by, xpath))
                    )
                
                    # Ensure that we have enough elements to access the desired index
                    if len(elements) <= index:
                        _logger.error(f"Not enough elements found for '{xpath}'. Expected at least {index + 1} elements.")
                        raise IndexError(f"Element at index {index} not found for '{xpath}'.")
                
                    # Ensure the element at the specified index is interactable and in viewport
                    element = self.wait_until_interactable(xpath, by)
                
                    if click_delay:
                        sleep(click_delay)
                
                    try:
                        elements[index].click()
                        _logger.info(f"Successfully clicked element at index {index}")
                        return elements[index]
                    except ElementClickInterceptedException as e:
                        _logger.error(
                            f'Failed to click "{xpath}" at index {index} due to ElementClickInterceptedException. Trying to click using JavaScript.',
                            exc_info=True,
                            stack_info=True,
                            extra={"screenshot": False},
                        )
                        self._driver.execute_script("arguments[0].click();", elements[index])
                        _logger.info(f"Successfully clicked element at index {index} using JavaScript")
                        return elements[index]
                        
                except Exception as e:
                    error_msg = str(e)
                    if "stale element" in error_msg.lower() and retry < max_retries - 1:
                        _logger.warning(f'Stale element on attempt {retry + 1}/{max_retries}, retrying...')
                        time.sleep(1)
                        continue
                    else:
                        _logger.error(
                            f'Failed to click "{xpath}" at index {index}. Element might not be interactable. Error: {error_msg[:200]}',
                            exc_info=True,
                            stack_info=True,
                            extra={"screenshot": True},
                        )
                        raise e
            
            raise Exception(f"Failed to click element after {max_retries} retries")


    def close_all_overlays(self):
        try:
            # Remove all cdk overlays just before any interaction
            self._driver.execute_script("""
                const overlays = document.querySelectorAll('.cdk-overlay-backdrop, .cdk-overlay-dark-backdrop, .cdk-overlay-pane');
                overlays.forEach(el => el.remove());
            """)
            _logger.info("Forcefully removed all cdk overlays.")
            time.sleep(0.5)  # Give DOM time to update
        except Exception as e:
            _logger.warning(f"Error removing overlays: {e}")


    def focus_and_send_text(self, xpath: str, text: str, by=By.XPATH) -> WebElement:
        _logger.info(f'Sending text "{text}" to "{xpath}"')
        element = self.click(xpath, by)
        element.send_keys(text)
        return element

    def upload_file(self, input_element_xpath: str, file_path: str) -> WebElement:
        _logger.info(f'Uploading "{file_path}" to element "{input_element_xpath}"')
        element = self.wait_until_exists(input_element_xpath)
        element.send_keys(file_path)
        return element

    def change_attribute(self, xpath: str, attribute: str, value: str, by=By.XPATH) -> None:
        _logger.info(f'Changing "{xpath}" attribute "{attribute}" to {value}')
        element = self.wait_until_exists(xpath, by)
        self._driver.execute_script(
            f'arguments[0].setAttribute("{attribute}", "{value}");', element
        )

    def change_value(self, xpath: str, value: str, by=By.XPATH) -> None:
        _logger.info(f'Changing "{xpath}" value to {value}')
        element = self.wait_until_exists(xpath, by)
        self._driver.execute_script(f'arguments[0].value = "{value}";', element)
        self._driver.execute_script(
            'arguments[0].dispatchEvent(new Event("input", { bubbles: true }));',
            element,
        )

    def select(self, xpath: str, visible_text: str, by=By.XPATH) -> None:
        _logger.info(f'Selecting "{visible_text}" in "{xpath}"')
        element = self.wait_until_interactable(xpath, by)
        Select(element).select_by_visible_text(visible_text)
        
    def get_text(self, locator: str, by=By.XPATH) -> str:
        # _logger.info(f'Getting text from element located by "{by}" with locator "{locator}"')
        element = self.wait_until_interactable(locator, by)
        text = element.text
        # _logger.info(f'Text found: "{text}"')
        return text
    
    def count_rows(self, table_selector=None, row_selector="//tbody//tr", skip_header=True) -> int:
        try:
            _logger.info(f"Counting rows using selector: {row_selector}")
            
            # Find all the <tr> elements within the <tbody>
            rows = self._driver.find_elements(By.XPATH, row_selector)
            
            # Get the count of rows
            row_count = len(rows)
            
            # Skip header row if requested and if there are rows
            if skip_header and row_count > 0:
                row_count -= 1
                
            _logger.info(f"Found {row_count} rows (excluding headers: {skip_header})")
            return row_count
        except Exception as e:
            _logger.error(f"Failed to count rows. Error: {str(e)}")
            self._driver.save_screenshot(f"./failed_to_count_rows_{int(time.time())}.png")
            return 0

    def switch_to_window(self, windows_index: int) -> None:
        _logger.info(f'Switching to window index {windows_index}')
        self._driver.switch_to.window(self._driver.window_handles[windows_index])

    def navigate(self, url: str) -> None:
        self._driver.get(url)

    def quit(self) -> None:
        self._driver.quit()

    @property
    def driver(self) -> webdriver.Chrome:
        return self._driver