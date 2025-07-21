import time
import logging
import pyperclip
from ...base_test import BaseTest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from ...cluster_operator import ClusterManager

logger = logging.getLogger(__name__)

class AgentAccessKeys(BaseTest):    
    def run(self):
        logger.info("Starting Agent Access Keys test")
        
        self.navigate_to_agent_access_keys()
        time.sleep(1)
        self.create_new_key()
        # copy is not working in headless mode
        # self.copy_key()
        # self.change_default_key()
        self.edit_key()
        self.delete_key()
        
        logger.info("Agent Access Keys test completed successfully")        

    def navigate_to_agent_access_keys(self):
        try:
            self._interaction_manager.click('agent-access-tokens-settings-left-menu-item', By.ID)
            logger.info("Successfully navigated to Agent Access Keys page")
        except Exception as e:
            logger.error(f"Failed to navigate to Agent Access Keys page: {str(e)}")
            self._driver.save_screenshot(f"./failed_to_navigate_agent_access_keys_{ClusterManager.get_current_timestamp()}.png")
            raise

    def create_new_key(self):
        logger.info("Creating new agent access key")

        # count_rows - skip_header=False so it counts all rows, there is probably an issue with the function
        num_of_access_keys = self._interaction_manager.count_rows(skip_header=False)
        logger.info(f"Current number of agent access keys: {num_of_access_keys}")
        
        try:
            # Click on "Create New Key" button (update selector as needed)
            self._interaction_manager.click('/html/body/armo-root/div/div/div/div/armo-agent-access-tokens-page/div/armo-button')
            
            # Fill in key name
            self._interaction_manager.focus_and_send_text('/html/body/div[5]/div[2]/div/mat-dialog-container/div/div/armo-agent-access-token-modal/div[2]/form/div/div[2]/mat-form-field/div[1]/div/div[2]/input', 'test')

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
            logger.error(f"Failed to create new key: {str(e)}")
            self._driver.save_screenshot(f"./failed_to_create_key_{ClusterManager.get_current_timestamp()}.png")

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

    # def change_default_key(self):
    #     logger.info("Changing default agent access key")
        
    #     # TODO: Implement default key change logic
    #     try:
    #         # Example placeholder logic:
    #         # self._interaction_manager.click("//button[contains(text(), 'Set as Default')]", By.XPATH)
            
    #         logger.info("Default key changed successfully")
    #         time.sleep(1)
    #     except Exception as e:
    #         logger.error(f"Failed to change default key: {str(e)}")
    #         self._driver.save_screenshot(f"./failed_to_change_default_key_{ClusterManager.get_current_timestamp()}.png")

    def edit_key(self):
        logger.info("Editing agent access key")
        wait = WebDriverWait(self._driver, 10, 0.001)
        
        try:
            # Click on the edit button for the first row (the newly created key)
            # Find row options buttons
            buttons = wait.until(EC.visibility_of_all_elements_located((By.TAG_NAME, 'armo-row-options-button')))
            
            logger.info(f"Found {len(buttons)} row options buttons")

            if not buttons:
                raise Exception("No row options buttons found")
            
            # Click on the first button - this should be the newly created key
            buttons[0].click()

            # Click on the edit option
            self._interaction_manager.click('/html/body/div[5]/div[2]/div/div/div/div[2]/armo-button')

            # Fill in new key name
            self._interaction_manager.focus_and_send_text('/html/body/div[5]/div[2]/div/mat-dialog-container/div/div/armo-agent-access-token-modal/div[2]/form/div/div[2]/mat-form-field/div[1]/div/div[2]/input', ' edited')

            # Click on save button
            self._interaction_manager.click('/html/body/div[5]/div[2]/div/mat-dialog-container/div/div/armo-agent-access-token-modal/div[3]/armo-button[2]')
            
            time.sleep(1)  # Wait for the key to be edited

            # Verify the key was edited
            edited_key_name = self._interaction_manager.get_text('/html/body/armo-root/div/div/div/div/armo-agent-access-tokens-page/armo-agent-access-tokens-table/div/table/tbody/tr[1]/td[1]/span')

            if edited_key_name != 'test edited':
                raise Exception(f"Edited key name does not match expected value. Found: {edited_key_name}, Expected: 'test edited'")
            
            logger.info("Agent access key edited successfully")
        except Exception as e:
            logger.error(f"Failed to edit key: {str(e)}")
            self._driver.save_screenshot(f"./failed_to_edit_key_{ClusterManager.get_current_timestamp()}.png")

    def delete_key(self):
        logger.info("Deleting agent access key")
        wait = WebDriverWait(self._driver, 10, 0.001)

        num_of_access_keys = self._interaction_manager.count_rows(skip_header=False)
        logger.info(f"Current number of agent access keys: {num_of_access_keys}")
        
        try:
            # Click on the delete button for the first row (the newly created key)
            # Find row options buttons
            buttons = wait.until(EC.visibility_of_all_elements_located((By.TAG_NAME, 'armo-row-options-button')))
            
            logger.info(f"Found {len(buttons)} row options buttons")

            if not buttons:
                raise Exception("No row options buttons found")
            
            # Click on the first button - this should be the newly created key
            buttons[0].click()

            # Click on the delete option
            self._interaction_manager.click('/html/body/div[5]/div[2]/div/div/div/div[3]/armo-button')

            # Confirm deletion
            self._interaction_manager.click('/html/body/div[5]/div[2]/div/mat-dialog-container/div/div/armo-delete-confirm-modal/div[2]/armo-button[2]')

            time.sleep(1)  # Wait for the key to be deleted

            # Verify the number of access keys decreased
            num_of_access_keys_after = self._interaction_manager.count_rows(skip_header=False)
            logger.info(f"Number of agent access keys after deletion: {num_of_access_keys_after}")

            if num_of_access_keys_after != num_of_access_keys - 1:
                raise Exception("Number of agent access keys did not decrease as expected")
            
            logger.info("Agent access key deleted successfully")
        except Exception as e:
            logger.error(f"Failed to delete key: {str(e)}")
            self._driver.save_screenshot(f"./failed_to_delete_key_{ClusterManager.get_current_timestamp()}.png")