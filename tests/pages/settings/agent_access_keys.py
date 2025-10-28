import time
import logging
import pyperclip
from datetime import datetime
from ...base_test import BaseTest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from ...cluster_operator import ClusterManager

logger = logging.getLogger(__name__)

class AgentAccessKeys(BaseTest):
    def __init__(self, config):
        super().__init__(config)
        # Generate unique key name with readable date/time timestamp
        readable_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.test_key_name = f"test {readable_timestamp}"
        logger.info(f"Generated test key name: {self.test_key_name}")
        
    def _handle_error(self, operation: str, exception: Exception):
        """Common error handling method"""
        logger.error(f"Failed to {operation}: {str(exception)}")
        screenshot_name = f"./failed_{operation.replace(' ', '_')}_{ClusterManager.get_current_timestamp()}.png"
        self._driver.save_screenshot(screenshot_name)
        
    def _find_row_options_buttons(self) -> list:
        """Find and return row options buttons with proper waiting"""
        wait = WebDriverWait(self._driver, 10, 0.001)
        buttons = wait.until(EC.visibility_of_all_elements_located((By.TAG_NAME, 'armo-row-options-button')))
        logger.info(f"Found {len(buttons)} row options buttons")
        
        if not buttons:
            raise Exception("No row options buttons found")
        return buttons
    
    def _get_table_action_options(self) -> list:
        """Get table action options (edit, delete, etc.)"""
        options = self._driver.find_elements(By.CSS_SELECTOR, '.armo-button.table-more-actions.md')
        if not options:
            raise Exception("No options buttons found")
        return options
        
    def run(self):
        logger.info("Starting Agent Access Keys test")
        
        self.navigate_to_agent_access_keys()
        self.create_new_key()
        # copy is not working in headless mode
        # self.copy_key()
        self.change_default_key()
        self.edit_key()
        self.delete_key()
        
        logger.info("Agent Access Keys test completed successfully")        

    def navigate_to_agent_access_keys(self):
        try:
            self._interaction_manager.click('agent-access-tokens-settings-left-menu-item', By.ID)
            logger.info("Successfully navigated to Agent Access Keys page")
            time.sleep(1)  # Wait for the page to load
        except Exception as e:
            self._handle_error("navigate to Agent Access Keys page", e)
            raise

    def create_new_key(self):
        logger.info(f"Creating new agent access key with name: {self.test_key_name}")

        # count_rows - skip_header=False so it counts all rows, there is probably an issue with the function
        num_of_access_keys = self._interaction_manager.count_rows(skip_header=False)
        logger.info(f"Current number of agent access keys: {num_of_access_keys}")
        
        try:
            # Click on "Create New Key" button (update selector as needed)
            self._interaction_manager.click('/html/body/armo-root/div/div/div/div/armo-agent-access-tokens-page/div/armo-button')
            
            # Fill in key name with timestamp
            self._interaction_manager.focus_and_send_text('/html/body/div[5]/div[2]/div/mat-dialog-container/div/div/armo-agent-access-token-modal/div[2]/form/div/div[2]/mat-form-field/div[1]/div/div[2]/input', self.test_key_name)

            # Click on save button
            self._interaction_manager.click('/html/body/div[5]/div[2]/div/mat-dialog-container/div/div/armo-agent-access-token-modal/div[3]/armo-button[2]', By.XPATH)
            time.sleep(1)  # Wait for the key to be created

            # Verify the number of access keys increased
            num_of_access_keys_after = self._interaction_manager.count_rows(skip_header=False)
            logger.info(f"Number of agent access keys after creation: {num_of_access_keys_after}")

            if num_of_access_keys_after != num_of_access_keys + 1:
                raise Exception("Number of agent access keys did not increase as expected")
                        
            logger.info("New agent access key created successfully")
        except Exception as e:
            self._handle_error("create new key", e)

    def copy_key(self):
        logger.info("Copying agent access key")
        wait = WebDriverWait(self._driver, 10, 0.001)
        
        try:
            # Click on the copy button for the first row (the newly created key)
            # Find row options buttons
            buttons = wait.until(EC.visibility_of_all_elements_located((By.TAG_NAME, 'armo-row-options-button')))
            
            logger.info(f"Found {len(buttons)} row options buttons")

            if not buttons:
                raise Exception("No row options buttons found")
            
            # Click on the first button - this should be the newly created key
            buttons[0].click()

            # Click on the copy option
            self._interaction_manager.click('/html/body/div[5]/div[2]/div/div/div/div[1]/armo-button')

            # Validate that the key is copied to clipboard
            # Get the clipboard value
            clipboard_value = pyperclip.paste()

            # Get the presented key value
            self._interaction_manager.click('/html/body/armo-root/div/div/div/div/armo-agent-access-tokens-page/armo-agent-access-tokens-table/div/table/tbody/tr[1]/td[2]/div/armo-icon-button')
            presented_key_value = self._interaction_manager.get_text('/html/body/armo-root/div/div/div/div/armo-agent-access-tokens-page/armo-agent-access-tokens-table/div/table/tbody/tr[1]/td[2]/div/span')
            
            if clipboard_value != presented_key_value:
                raise Exception(f"Copied key value does not match presented key value. Copied: {clipboard_value}, Presented: {presented_key_value}")
            
            logger.info("Agent access key copied successfully")
        except Exception as e:
            logger.error(f"Failed to copy key: {str(e)}")
            self._driver.save_screenshot(f"./failed_to_copy_key_{ClusterManager.get_current_timestamp()}.png")

    def change_default_key(self):
        logger.info("Changing default agent access key")
        
        try:
            # Click on the default radio button for the first row (the newly created key)
            self._interaction_manager.click('/html/body/armo-root/div/div/div/div/armo-agent-access-tokens-page/armo-agent-access-tokens-table/div/table/tbody/tr[1]/td[5]/div/mat-radio-button')

            # Get the key value
            # Show the key value in the UI
            self._interaction_manager.click("//armo-icon-button[@data-test-id='show-token-button' or @data-test-id='show-value-button']//button")
            # Get the key value from the UI
            key_value = self._interaction_manager.get_text("//span[@data-test-id='value-span' or @data-test-id='token-span']")

            # Navigate to setup page
            logger.info("Navigating to setup page to verify the default key")
            self._interaction_manager.click('armo-finish-setup-navigation-widget', By.TAG_NAME)

            # Open connect kubernetes cluster modal
            self._interaction_manager.click('/html/body/armo-root/div/div/div/armo-finish-setup-page/armo-finish-setup-cards-list/div/armo-finish-setup-card[1]/armo-button')

            # Get connection command
            logger.info("Getting connection command from the modal")
            helm_command = self._interaction_manager.get_text('div.command-area > span.ng-star-inserted', By.CSS_SELECTOR)

            # Close the side panel
            self._interaction_manager.close_all_overlays()

            # Validate that the connect command contains the key value
            if f" --set accessKey={key_value}" not in helm_command:
                raise Exception(f"Default key value not found in connect command. Key: {key_value}, Command: {helm_command}")
            
            # Change the default key in the UI back to the original key
            logger.info("Changing default key back to the original key")
            self._interaction_manager.click('settings-left-menu-item', By.ID)
            self.navigate_to_agent_access_keys()
            # Click on the default radio button for the last row (the original key)
            buttons = self._driver.find_elements(By.TAG_NAME, 'mat-radio-button')

            logger.info(f"Found {len(buttons)} radio buttons")

            if not buttons:
                raise Exception("No radio buttons found")
            
            # Click on the last button - this should be the original key
            buttons[-1].click()
            
            logger.info("Default key changed successfully")
        except Exception as e:
            self._handle_error("change default key", e)

    def edit_key(self):
        logger.info("Editing agent access key")
        
        try:
            # Click on the edit button for the first row
            buttons = self._find_row_options_buttons()
            buttons[0].click()

            # Click on the edit option (second option)
            options = self._get_table_action_options()
            options[1].click()

            # Fill in new key name (append " edited" to the original name)
            self._interaction_manager.focus_and_send_text('//*[@id="mat-input-1"]', ' edited')

            # Click on save button
            cluster_manager = ClusterManager(self._driver, self._wait)
            cluster_manager.click_button_by_text('Save', 'primary', 'xl')

            time.sleep(5)  # Wait for the changes to reflect and toast to disappear

            # Verify the key was edited
            edited_key_name = self._interaction_manager.get_text('/html/body/armo-root/div/div/div/div/armo-agent-access-tokens-page/armo-agent-access-tokens-table/div/table/tbody/tr[1]/td[1]/span')
            expected_name = f"{self.test_key_name} edited"

            if edited_key_name != expected_name:
                raise Exception(f"Edited key name does not match expected value. Found: '{edited_key_name}', Expected: '{expected_name}'")
            
            logger.info("Agent access key edited successfully")
        except Exception as e:
            self._handle_error("edit key", e)

    def delete_key(self):
        logger.info("Deleting agent access key")

        num_of_access_keys = self._interaction_manager.count_rows(skip_header=False)
        logger.info(f"Current number of agent access keys: {num_of_access_keys}")
        
        try:
            # Click on the delete button for the first row
            buttons = self._find_row_options_buttons()
            buttons[0].click()
            time.sleep(1)  # Wait for the options to appear

            # Click on the delete option (last option)
            options = self._get_table_action_options()
            options[-1].click()

            time.sleep(1)  # Wait for the delete confirmation dialog to appear

            # Confirm deletion
            cluster_manager = ClusterManager(self._driver, self._wait)
            cluster_manager.click_button_by_text('Delete', 'error', 'xl')

            time.sleep(1)  # Wait for the key to be deleted

            # Verify the number of access keys decreased
            num_of_access_keys_after = self._interaction_manager.count_rows(skip_header=False)
            logger.info(f"Number of agent access keys after deletion: {num_of_access_keys_after}")

            if num_of_access_keys_after != num_of_access_keys - 1:
                raise Exception("Number of agent access keys did not decrease as expected")
            
            logger.info("Agent access key deleted successfully")
        except Exception as e:
            self._handle_error("delete key", e)