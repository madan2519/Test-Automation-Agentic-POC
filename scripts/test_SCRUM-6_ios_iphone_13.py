# Import necessary libraries
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Define the desired capabilities for iPhone 13
desired_capabilities = {
    "platformName": "iOS",
    "platformVersion": "15.0",
    "deviceName": "iPhone 13",
    "browserName": "Safari",
    "automationName": "XCUITest"
}

# Set up the Appium driver
driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_capabilities)

# Open the URL in the URL bar
driver.get("https://demoqa.com/")

# Check for elements tile available in the page and click the tile
elements_tile = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((AppiumBy.XPATH, "//h5[text()='Elements']"))
)
elements_tile.click()

# User will land to https://demoqa.com/elements
# Left side navigation will be there and check for text Text Box and click on the text
text_box = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((AppiumBy.XPATH, "//li[text()='Text Box']"))
)
text_box.click()

# Add the below details:
# Full Name - Roopak Mahajan
# Email - roopakmahajan1992@gmail.com
# Current Address - keshav puram
# Permanent Address - keshav puram
full_name_input = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((AppiumBy.ID, "userName"))
)
full_name_input.send_keys("Roopak Mahajan")

email_input = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((AppiumBy.ID, "userEmail"))
)
email_input.send_keys("roopakmahajan1992@gmail.com")

current_address_input = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((AppiumBy.ID, "currentAddress"))
)
current_address_input.send_keys("keshav puram")

permanent_address_input = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((AppiumBy.ID, "permanentAddress"))
)
permanent_address_input.send_keys("keshav puram")

# Click on submit button
submit_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((AppiumBy.ID, "submit-btn"))
)
submit_button.click()

# Wait for 5 seconds before closing the driver
time.sleep(5)

# Close the driver
driver.quit()