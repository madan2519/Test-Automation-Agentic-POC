# Import necessary libraries
from appium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Define desired capabilities for iPhone 13
desired_capabilities = {
    'platformName': 'iOS',
    'platformVersion': '15.0',
    'deviceName': 'iPhone 13',
    'browserName': 'Safari',
    'automationName': 'XCUITest'
}

# Set up Appium WebDriver
driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_capabilities)

# Step 1: Open URL in the URL bar
def open_url(url):
    driver.get(url)

# Step 2: Check for elements tile available in the page and click the tile
def click_elements_tile():
    elements_tile = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//h5[text()='Elements']"))
    )
    elements_tile.click()

# Step 3: Check for text Text Box and click on the text
def click_text_box():
    text_box = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//span[text()='Text Box']"))
    )
    text_box.click()

# Step 4: Add details
def add_details():
    full_name_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "userName"))
    )
    full_name_input.send_keys("Roopak Mahajan")

    email_input = driver.find_element(By.ID, "userEmail")
    email_input.send_keys("roopakmahajan1992@gmail.com")

    current_address_input = driver.find_element(By.ID, "currentAddress")
    current_address_input.send_keys("keshav puram")

    permanent_address_input = driver.find_element(By.ID, "permanentAddress")
    permanent_address_input.send_keys("keshav puram")

# Step 5: Click on submit button
def click_submit_button():
    submit_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "submit"))
    )
    submit_button.click()

# Main function
def main():
    url = "https://demoqa.com/"
    open_url(url)
    click_elements_tile()
    click_text_box()
    add_details()
    click_submit_button()
    time.sleep(5)  # Wait for 5 seconds before closing the browser
    driver.quit()

if __name__ == "__main__":
    main()