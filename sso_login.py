import time
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def main(SSO_MAIL, SSO_PASSWORD):
    URL = 'https://auth.armosec.io/oauth/account/login'
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)  
    driver.get(URL)
    
    def get_shadow_root():
        """Helper function to get shadow root if present"""
        try:
            shadow_host = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "frontegg-login-box-container-default"))
            )
            return driver.execute_script("return arguments[0].shadowRoot", shadow_host)
        except TimeoutException:
            print("Shadow root not found. Proceeding with direct login.")
            return None  

    shadow_root = get_shadow_root()
    
    if shadow_root:
        # Frontegg login with Shadow DOM
        email_input = WebDriverWait(driver, 10).until(
            lambda d: get_shadow_root().find_element(By.CSS_SELECTOR, "input[name='identifier']")
        )
        email_input.send_keys(SSO_MAIL)
        email_input.send_keys(Keys.ENTER)
    else:
        # Microsoft login directly
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "i0116"))
        )
        email_input.send_keys(SSO_MAIL)
        email_input.send_keys(Keys.ENTER)

    # Handle Password Input in Microsoft Login**
    try:
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "i0118"))  # Use the confirmed ID
        )
        password_input.send_keys(SSO_PASSWORD)
        password_input.send_keys(Keys.ENTER)
        print("Entered password successfully.")
    except TimeoutException:
        print("Failed to find password field.")
        driver.save_screenshot("./failed_to_find_password_field.png")
        driver.quit()
        exit(1)

    #Click "Yes" Button if Present**
    try:
        yes_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "idSIButton9"))
        )
        yes_button.click()
        print("Clicked on 'Yes' button to stay signed in.")
    except TimeoutException:
        print("No 'Yes' button found. Skipping.")

    #Verify Successful Login**
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "configuration-scanning-left-menu-item"))
        )
        print("SSO Login successful!")
    except TimeoutException:
        print("Login failed. Taking screenshot...")
        driver.save_screenshot("./failed_to_login.png")
        driver.quit()
        exit(1)

    driver.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='SSO Login Script')
    parser.add_argument('--email', type=str, required=True, help='The email address for SSO login')
    parser.add_argument('--password', type=str, required=True, help='The password for SSO login')
    args = parser.parse_args()
    main(args.email, args.password)
