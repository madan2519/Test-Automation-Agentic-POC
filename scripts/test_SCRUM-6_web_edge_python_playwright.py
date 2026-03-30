# Import the required libraries
from playwright.sync_api import sync_playwright
import pytest

# Define the test function
def test_demosite():
    # Launch the browser
    with sync_playwright() as p:
        # Launch the Edge browser
        browser = p.chromium.launch(headless=False, channel="msedge")
        # Create a new browser context
        context = browser.new_context()
        # Create a new page
        page = context.new_page()

        # Open the URL
        page.goto("https://demoqa.com/")

        # Check for elements tile and click on it
        elements_tile = page.query_selector("text=Elements")
        assert elements_tile is not None
        elements_tile.click()

        # Wait for the navigation to complete
        page.wait_for_url("https://demoqa.com/elements")

        # Check for Text Box and click on it
        text_box = page.query_selector("text=Text Box")
        assert text_box is not None
        text_box.click()

        # Fill in the form details
        full_name_input = page.query_selector("#userName")
        full_name_input.fill("Roopak Mahajan")

        email_input = page.query_selector("#userEmail")
        email_input.fill("roopakmahajan1992@gmail.com")

        current_address_input = page.query_selector("#currentAddress")
        current_address_input.fill("keshav puram")

        permanent_address_input = page.query_selector("#permanentAddress")
        permanent_address_input.fill("keshav puram")

        # Click the submit button
        submit_button = page.query_selector("#submit")
        submit_button.click()

        # Close the browser
        browser.close()

# Run the test function
test_demosite()