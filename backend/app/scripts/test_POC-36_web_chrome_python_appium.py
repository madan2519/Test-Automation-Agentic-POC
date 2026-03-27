from appium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import unittest

class ContactListAppTest(unittest.TestCase):

    def setUp(self):
        # Set up Appium
        desired_caps = {
            'platformName': 'Windows',
            'browserName': 'Chrome',
            'version': 'latest',
            'automationName': 'Appium',
            'newCommandTimeout': 6000
        }
        self.driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
        self.driver.get('http://example.com/contact-list-app')  # Replace with actual URL

    def test_user_authentication(self):
        # Test AC001: User Registration
        self.driver.get('http://example.com/register')  # Replace with actual registration page URL
        self.driver.find_element(By.ID, 'username').send_keys('testuser')
        self.driver.find_element(By.ID, 'password').send_keys('password123')
        self.driver.find_element(By.ID, 'register').click()
        success_message = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'success-message'))
        )
        self.assertIn('registered successfully', success_message.text)

        # Test AC002: User Login
        self.driver.get('http://example.com/login')  # Replace with actual login page URL
        self.driver.find_element(By.ID, 'username').send_keys('testuser')
        self.driver.find_element(By.ID, 'password').send_keys('password123')
        self.driver.find_element(By.ID, 'login').click()
        welcome_message = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'welcome-message'))
        )
        self.assertIn('logged in successfully', welcome_message.text)

        # Test AC003: Invalid Login
        self.driver.find_element(By.ID, 'username').send_keys('wronguser')
        self.driver.find_element(By.ID, 'password').send_keys('wrongpassword')
        self.driver.find_element(By.ID, 'login').click()
        error_message = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'error-message'))
        )
        self.assertIn('error', error_message.text)

    def test_contact_management(self):
        # Assume user is already logged in
        self.driver.get('http://example.com/contacts')  # Replace with actual contacts page URL

        # Test AC004: Add Contact
        self.driver.find_element(By.ID, 'add-contact').click()
        self.driver.find_element(By.ID, 'contact-name').send_keys('John Doe')
        self.driver.find_element(By.ID, 'contact-phone').send_keys('1234567890')
        self.driver.find_element(By.ID, 'save-contact').click()
        contact_added_message = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'contact-added-message'))
        )
        self.assertIn('added successfully', contact_added_message.text)

        # Test AC005: Edit Contact
        self.driver.find_element(By.ID, 'edit-contact').click()
        self.driver.find_element(By.ID, 'contact-name').clear()
        self.driver.find_element(By.ID, 'contact-name').send_keys('Jane Doe')
        self.driver.find_element(By.ID, 'save-contact').click()
        contact_updated_message = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'contact-updated-message'))
        )
        self.assertIn('updated successfully', contact_updated_message.text)

        # Test AC006: Delete Contact
        self.driver.find_element(By.ID, 'delete-contact').click()
        contact_deleted_message = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'contact-deleted-message'))
        )
        self.assertIn('deleted successfully', contact_deleted_message.text)

        # Test AC007: View Contacts
        contacts_list = self.driver.find_elements(By.CLASS_NAME, 'contact-item')
        self.assertGreater(len(contacts_list), 0)

        # Test AC008: Add Contact with Invalid Details
        self.driver.find_element(By.ID, 'add-contact').click()
        self.driver.find_element(By.ID, 'contact-name').send_keys('')
        self.driver.find_element(By.ID, 'contact-phone').send_keys('invalidphone')
        self.driver.find_element(By.ID, 'save-contact').click()
        error_message = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'error-message'))
        )
        self.assertIn('error', error_message.text)

        # Test AC009: Edit Contact with Invalid Details
        self.driver.find_element(By.ID, 'edit-contact').click()
        self.driver.find_element(By.ID, 'contact-name').clear()
        self.driver.find_element(By.ID, 'contact-name').send_keys('')
        self.driver.find_element(By.ID, 'save-contact').click()
        error_message = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'error-message'))
        )
        self.assertIn('error', error_message.text)

    def test_data_persistence(self):
        # Test AC010: Data Persistence after Refresh/Re-login
        self.driver.get('http://example.com/contacts')  # Assume user is logged in
        self.driver.refresh()
        contacts_list = self.driver.find_elements(By.CLASS_NAME, 'contact-item')
        self.assertGreater(len(contacts_list), 0)

    def test_access_control(self):
        # Test AC011: Access Control
        self.driver.get('http://example.com/contacts')  # User not logged in
        login_page = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'login-page'))
        )
        self.assertTrue(login_page.is_displayed())

    def tearDown(self):
        self.driver.quit()

if __name__ == '__main__':
    unittest.main()