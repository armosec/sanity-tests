import logging
from time import sleep
from typing import Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import ElementClickInterceptedException

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

    def click(self, xpath: str, by=By.XPATH, click_delay: Optional[float] = None, index: int = 0) -> WebElement:
        _logger.info(f'Clicking "{xpath}" at index {index}')
    
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
        except ElementClickInterceptedException as e:
            _logger.error(
                f'Failed to click "{xpath}" at index {index} due to ElementClickInterceptedException. Trying to click using JavaScript.',
                exc_info=True,
                stack_info=True,
                extra={"screenshot": False},
            )
            self._driver.execute_script("arguments[0].click();", elements[index])
        except Exception as e:
            _logger.error(
                f'Failed to click "{xpath}" at index {index}. Element might not be interactable.',
                exc_info=True,
                stack_info=True,
                extra={"screenshot": True},  # Take a screenshot on error
            )
            raise e
    
        return elements[index]


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
    
    def count_rows(self) -> int:
        try:
            # Find all the <tr> elements within the <tbody> (replace with your actual <tbody> locator if necessary)
            rows = self.driver.find_elements(By.XPATH, "//tbody//tr")
            
            # Get the count of rows
            row_count = len(rows)
            return row_count
        except Exception as e:
            _logger.error(f"Failed to count rows. Error: {str(e)}")
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
