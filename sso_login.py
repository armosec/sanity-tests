import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def main(SSO_MAIL, SSO_PASSWORD):
    # Define the elements
    EMAILFIELD = (By.XPATH, '//*[@id="frontegg-login-box-container-default"]/div[1]/input')
    PASSWORDFIELD = (By.ID, "i0118")
    NEXTBUTTON = (By.ID, "idSIButton9")
    URL = 'https://auth.armosec.io/oauth/account/login'
    
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    driver = webdriver.Chrome(options=chrome_options)  
    driver.get(URL)
    
    # Wait for email field, enter email, and then press Enter
    email_field = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(EMAILFIELD))
    email_field.send_keys(SSO_MAIL + Keys.ENTER)
    
    password_field = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(PASSWORDFIELD))
    password_field.send_keys(SSO_PASSWORD)
    password_field.send_keys(Keys.ENTER) # Press Enter to login
    time.sleep(1)  
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(NEXTBUTTON)).click() # Click the next button
    
    # Wait for the element to appear to verify the login
    try:
        element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "configuration-scanning-left-menu-item"))
        )
        print("SSO Login pass successful.")
    except TimeoutException:
        print("Login failed. Element does not exist within the given time frame.")
        driver.save_screenshot("faild_to_login.png")
        exit(1)
    
    driver.quit()

if __name__ == "__main__":
    # Check if the correct number of arguments are provided
    if len(sys.argv) != 3:
        print("Usage: python script.py <SSO_MAIL> <SSO_PASSWORD>")
        sys.exit(1)
    
    SSO_MAIL = sys.argv[1]
    SSO_PASSWORD = sys.argv[2]

    main(SSO_MAIL, SSO_PASSWORD)
