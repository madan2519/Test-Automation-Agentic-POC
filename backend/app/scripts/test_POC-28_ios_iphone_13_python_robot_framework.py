from appium import webdriver
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import string

def random_string(length=6):
    """Generate a random string of fixed length"""
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))

# Desired capabilities for iPhone 13
desired_caps = {
    'platformName': 'iOS',
    'platformVersion': '15.0',  # Update this to the actual version if needed
    'deviceName': 'iPhone 13',
    'browserName': 'Safari',
    'automationName': 'XCUITest'
}

# Initialize the driver
driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)

try:
    # Open the application URL in the browser
    driver.get('https://thinking-tester-contact-list.herokuapp.com/')

    # Verify the Login page is displayed
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((MobileBy.XPATH, "//h1[text()='Login']"))
    )

    # Enter Email
    email_field = driver.find_element(MobileBy.XPATH, "//input[@type='email']")
    email_field.send_keys('madan25@gmail.com')

    # Enter Password
    password_field = driver.find_element(MobileBy.XPATH, "//input[@type='password']")
    password_field.send_keys('Madan@2519')

    # Click on Submit
    submit_button = driver.find_element(MobileBy.XPATH, "//button[text()='Submit']")
    submit_button.click()

    # Verify the page redirects to the Contact List page
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((MobileBy.XPATH, "//h1[text()='Contact List']"))
    )

    # Click on "Add a New Contact" button
    add_contact_button = driver.find_element(MobileBy.XPATH, "//button[text()='Add a New Contact']")
    add_contact_button.click()

    # Fill all mandatory fields with valid random details
    first_name = random_string()
    last_name = random_string()

    first_name_field = driver.find_element(MobileBy.XPATH, "//input[@placeholder='First Name']")
    first_name_field.send_keys(first_name)

    last_name_field = driver.find_element(MobileBy.XPATH, "//input[@placeholder='Last Name']")
    last_name_field.send_keys(last_name)

    # Click on Submit
    submit_contact_button = driver.find_element(MobileBy.XPATH, "//button[text()='Submit']")
    submit_contact_button.click()

    # Verify that the newly added contact appears in the Contact List table
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((MobileBy.XPATH, f"//td[text()='{first_name}']"))
    )
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((MobileBy.XPATH, f"//td[text()='{last_name}']"))
    )

    print("Test Passed: New contact added successfully and visible in the contact list.")

finally:
    # Quit the driver
    driver.quit()