import pytest
from playwright.sync_api import sync_playwright

def test_add_new_contact():
    with sync_playwright() as p:
        # Launch the browser
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # Open the application URL
        page.goto("https://thinking-tester-contact-list.herokuapp.com/")

        # Verify the Login page is displayed
        assert page.title() == "Login"

        # Enter Email and Password
        page.fill("input[name='email']", "madan25@gmail.com")
        page.fill("input[name='password']", "Madan@2519")

        # Click on Submit
        page.click("button[type='submit']")

        # Verify the page redirects to the Contact List page
        assert page.url == "https://thinking-tester-contact-list.herokuapp.com/contact-list"

        # Click on "Add a New Contact" button
        page.click("text='Add a New Contact'")

        # Fill all mandatory fields with valid random details
        page.fill("input[name='firstName']", "John")
        page.fill("input[name='lastName']", "Doe")

        # Click on Submit
        page.click("button[type='submit']")

        # Verify that the newly added contact appears in the Contact List table
        page.wait_for_selector("text='John Doe'")
        assert page.is_visible("text='John Doe'")

        # Close the browser
        browser.close()

if __name__ == "__main__":
    pytest.main(["-v", __file__])