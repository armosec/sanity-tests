import logging
from time import sleep
from typing import Optional

from .selenium_config import InteractionManagerConfig
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import ElementClickInterceptedException


_logger = logging.getLogger(__name__)


class InteractionManager:
    _driver: webdriver.Chrome
    _config: InteractionManagerConfig
    _timeout: int

    def __init__(self, config: InteractionManagerConfig):
        self._driver = self._initialize_driver(config)
        self._config = config
        self._timeout = self._config.timeout

    @staticmethod
    def _initialize_driver(config: InteractionManagerConfig) -> webdriver.Chrome:
        chrome_options = webdriver.ChromeOptions()

        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1280,800")
        chrome_options.add_argument("--allow-insecure-localhost")

        if config.headless:
            chrome_options.add_argument("--headless")
            chrome_options.add_experimental_option("detach", True)

        return webdriver.Chrome(options=chrome_options)

    def wait_until_interactable(self, xpath: str) -> WebElement:
        """
        Wait until an element can be interacted with. If it is not inside the screen,
        scroll into it.
        """
        element = WebDriverWait(self._driver, self._timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )

        WebDriverWait(self._driver, self._timeout).until(
            EC.visibility_of_element_located((By.XPATH, xpath))
        )

        scroll_to_element = """
        const element = arguments[0]
        function scrollToElement(element) {
            const elementRect = element.getBoundingClientRect();
            const windowWidth = window.innerWidth || document.documentElement.clientWidth;
            const windowHeight = window.innerHeight || document.documentElement.clientHeight;
            const scrollXTo = Math.max(elementRect.x - ((windowWidth - elementRect.width) / 2) + window.pageXOffset, 0);
            const scrollYTo = Math.max(elementRect.y - ((windowHeight - elementRect.height) / 2) + window.pageYOffset, 0);
            
            console.log(scrollXTo, scrollYTo, elementRect);
            window.scroll({
            left: scrollXTo,
            top: scrollYTo,
            behavior: 'auto'
            });
        }
        
        scrollToElement(element);
        """
        self._driver.execute_script(scroll_to_element, element)
        self._driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", element)

        WebDriverWait(self._driver, self._timeout).until(
            lambda driver: driver.execute_script(
                "return arguments[0].getBoundingClientRect().height > 0 && arguments[0].getBoundingClientRect().bottom <= window.innerHeight;",
                element,
            )
        )

        return element

    def wait_until_exists(self, xpath: str, timeout: Optional[int] = None):
        """
        Wait until an element exists on the DOM
        """
        if not timeout:
            timeout = self._timeout
        element = WebDriverWait(self._driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        return element

    def click(self, xpath: str, click_delay: Optional[float] = None) -> WebElement:
        _logger.info(f'Clicking "{xpath}"')
        if click_delay:
            sleep(click_delay)

        element = self.wait_until_interactable(xpath)
        try:
            if click_delay:
                sleep(click_delay)
            element.click()
        except ElementClickInterceptedException as e:
            _logger.error(
                f'Failed to click "{xpath}" due to ElementClickInterceptedException. Trying to click using JavaScript.',
                exc_info=True,
                stack_info=True,
                extra={"screenshot": False},
            )
            self._driver.execute_script("arguments[0].click();", element)

        return element

    def focus_and_send_text(self, xpath: str, text: str) -> WebElement:
        _logger.info(f'Sending text "{text}" to "{xpath}"')
        element = self.click(xpath)
        element.send_keys(text)
        return element

    def upload_file(self, input_element_xpath: str, file_path: str) -> WebElement:
        _logger.info(
            f'Uploading "{file_path}" to element "{input_element_xpath}"')
        element = self.wait_until_exists(input_element_xpath)
        element.send_keys(file_path)
        return element

    def change_attribute(self, xpath: str, attribute: str, value: str) -> None:
        _logger.info(f'Changing "{xpath}" attribute "{attribute}" to {value}')
        element = self.wait_until_exists(xpath)
        self._driver.execute_script(
            f'arguments[0].setAttribute("{attribute}", "{value}");', element
        )

    def change_value(self, xpath: str, value: str) -> None:
        _logger.info(f'Changing "{xpath}" value to {value}')
        element = self.wait_until_exists(xpath)

        self._driver.execute_script(
            f'arguments[0].value = "{value}";', element)
        self._driver.execute_script(
            'arguments[0].dispatchEvent(new Event("input", { bubbles: true }));',
            element,
        )

    def select(self, xpath: str, visible_text: str) -> None:
        _logger.info(f'Selecting "{visible_text}" in "{xpath}"')
        element = self.wait_until_interactable(xpath)
        Select(element).select_by_visible_text(visible_text)

    def switch_to_window(self, windows_index: int) -> None:
        _logger.info(f'Switching to window index {windows_index}')
        self._driver.switch_to.window(
            self._driver.window_handles[windows_index])

    def navigate(self, url: str) -> None:
        self._driver.get(url)

    def quit(self) -> None:
        self._driver.quit()

    @property
    def driver(self) -> webdriver.Chrome:
        return self._driver
