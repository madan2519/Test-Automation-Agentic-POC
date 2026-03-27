from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
import time

# Desired capabilities for iPhone 13
desired_caps = {
    'platformName': 'iOS',
    'platformVersion': '15.0',  # Update to the actual version of the iPhone 13
    'deviceName': 'iPhone 13',
    'browserName': 'Safari',
    'automationName': 'XCUITest'
}

# Initialize the Appium driver
driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)

try:
    # Open the application URL in the browser
    driver.get('https://thinking-tester-contact-list.herokuapp.com/')

    # Wait for the page to load
    time.sleep(3)

    # Verify the Login page is displayed
    assert "Login" in driver.title

    # Enter Email
    email_field = driver.find_element(AppiumBy.XPATH, '//input[@type="email"]')
    email_field.send_keys('madan25@gmail.com')

    # Enter Password
    password_field = driver.find_element(AppiumBy.XPATH, '//input[@type="password"]')
    password_field.send_keys('Madan@2519')

    # Click on Submit
    submit_button = driver.find_element(AppiumBy.XPATH, '//button[text()="Submit"]')
    submit_button.click()

    # Wait for redirection to Contact List page
    time.sleep(3)

    # Verify the page redirects to the Contact List page
    assert "Contact List" in driver.title

    # Click on "Add a New Contact" button
    add_contact_button = driver.find_element(AppiumBy.XPATH, '//button[text()="Add a New Contact"]')
    add_contact_button.click()

    # Wait for the Add Contact form to appear
    time.sleep(2)

    # Fill all mandatory fields with valid random details
    first_name_field = driver.find_element(AppiumBy.XPATH, '//input[@name="firstName"]')
    first_name_field.send_keys('John')

    last_name_field = driver.find_element(AppiumBy.XPATH, '//input[@name="lastName"]')
    last_name_field.send_keys('Doe')

    # Click on Submit
    submit_contact_button = driver.find_element(AppiumBy.XPATH, '//button[text()="Submit"]')
    submit_contact_button.click()

    # Wait for the contact to be added
    time.sleep(3)

    # Verify that the newly added contact appears in the Contact List table
    contact_list = driver.find_element(AppiumBy.XPATH, '//table[@id="contact-list"]')
    assert 'John Doe' in contact_list.text

finally:
    # Quit the driver
    driver.quit()