# Import necessary libraries
from appium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Define the desired capabilities for iPhone 13
desired_capabilities = {
    'platformName': 'iOS',
    'platformVersion': '15.0',
    'deviceName': 'iPhone 13',
    'browserName': 'Safari',
    'automationName': 'XCUITest'
}

# Set up the Appium server URL
appium_server_url = 'http://localhost:4723/wd/hub'

# Create a new instance of the WebDriver
driver = webdriver.Remote(command_executor=appium_server_url, desired_capabilities=desired_capabilities)

# Open the URL in the URL bar
driver.get('https://demoqa.com/')

# Check for elements tile available in the page and click the tile
try:
    elements_tile = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//h5[text()="Elements"]'))
    )
    elements_tile.click()
except Exception as e:
    print(f"Failed to find elements tile: {e}")

# Check if the user landed on the correct page
try:
    current_url = driver.current_url
    assert current_url == 'https://demoqa.com/elements'
    print("User landed on the correct page")
except Exception as e:
    print(f"Failed to land on the correct page: {e}")

# Check for text Text Box and click on the text
try:
    text_box_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//span[text()="Text Box"]'))
    )
    text_box_link.click()
except Exception as e:
    print(f"Failed to find text box link: {e}")

# Add the details
try:
    full_name_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, 'userName'))
    )
    full_name_input.send_keys('Roopak Mahajan')

    email_input = driver.find_element(By.ID, 'userEmail')
    email_input.send_keys('roopakmahajan1992@gmail.com')

    current_address_input = driver.find_element(By.ID, 'currentAddress')
    current_address_input.send_keys('keshav puram')

    permanent_address_input = driver.find_element(By.ID, 'permanentAddress')
    permanent_address_input.send_keys('keshav puram')

    submit_button = driver.find_element(By.ID, 'submit')
    submit_button.click()
except Exception as e:
    print(f"Failed to add details: {e}")

# Wait for 5 seconds before closing the browser
time.sleep(5)

# Close the browser
driver.quit()