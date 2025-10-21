from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def initialize_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new") 
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_window_size(1920, 1080)  # Set a standard window size for headless mode
    # driver.maximize_window()
    return driver
