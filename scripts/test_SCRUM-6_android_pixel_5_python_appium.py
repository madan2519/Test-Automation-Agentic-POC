# Import necessary libraries
from appium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Define the desired capabilities for the Android device
desired_capabilities = {
    'platformName': 'Android',
    'platformVersion': '11',
    'deviceName': 'Pixel 5',
    'browserName': 'Chrome',
    'chromedriverExecutable': '/path/to/chromedriver'
}

# Set up the Appium server URL
appium_server_url = 'http://localhost:4723/wd/hub'

# Create a new instance of the Chrome driver
driver = webdriver.Remote(command_executor=appium_server_url, desired_capabilities=desired_capabilities)

# Open the URL in the browser
driver.get('https://demoqa.com/')

# Wait for the elements tile to be clickable
try:
    elements_tile = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//h5[text()="Elements"]'))
    )
    elements_tile.click()
except TimeoutException:
    print("Elements tile not found")
    driver.quit()

# Wait for the Text Box link to be clickable
try:
    text_box_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//li[@id="item-0"]'))
    )
    text_box_link.click()
except TimeoutException:
    print("Text Box link not found")
    driver.quit()

# Fill in the form details
try:
    full_name_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'userName'))
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
except TimeoutException:
    print("Form not found")
    driver.quit()

# Close the browser
driver.quit()