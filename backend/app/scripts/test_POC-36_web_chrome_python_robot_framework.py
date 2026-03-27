import pytest
from playwright.sync_api import sync_playwright, expect

@pytest.fixture(scope="function")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        yield page
        context.close()
        browser.close()

def test_user_registration(browser):
    # AC001: User Registration
    browser.goto("https://thinking-tester-contact-list.herokuapp.com/register")
    browser.fill("input[name='username']", "testuser")
    browser.fill("input[name='password']", "password123")
    browser.fill("input[name='confirmPassword']", "password123")
    browser.click("button[type='submit']")
    expect(browser).to_have_url("https://thinking-tester-contact-list.herokuapp.com/login")

def test_user_login(browser):
    # AC002: User Login with valid credentials
    browser.goto("https://thinking-tester-contact-list.herokuapp.com/login")
    browser.fill("input[name='username']", "testuser")
    browser.fill("input[name='password']", "password123")
    browser.click("button[type='submit']")
    expect(browser).to_have_url("https://thinking-tester-contact-list.herokuapp.com/contacts")

def test_user_login_invalid(browser):
    # AC003: User Login with invalid credentials
    browser.goto("https://thinking-tester-contact-list.herokuapp.com/login")
    browser.fill("input[name='username']", "wronguser")
    browser.fill("input[name='password']", "wrongpassword")
    browser.click("button[type='submit']")
    expect(browser.locator(".error-message")).to_have_text("Invalid username or password")

def test_add_contact(browser):
    # AC004: Add a new contact
    test_user_login(browser)  # Ensure user is logged in
    browser.click("text='Add Contact'")
    browser.fill("input[name='name']", "John Doe")
    browser.fill("input[name='phone']", "1234567890")
    browser.fill("input[name='email']", "john.doe@example.com")
    browser.click("button[type='submit']")
    expect(browser.locator("text='John Doe'")).to_be_visible()

def test_edit_contact(browser):
    # AC005: Edit an existing contact
    test_user_login(browser)  # Ensure user is logged in
    browser.click("text='Edit' >> nth=0")
    browser.fill("input[name='name']", "Jane Doe")
    browser.click("button[type='submit']")
    expect(browser.locator("text='Jane Doe'")).to_be_visible()

def test_delete_contact(browser):
    # AC006: Delete an existing contact
    test_user_login(browser)  # Ensure user is logged in
    browser.click("text='Delete' >> nth=0")
    expect(browser.locator("text='Jane Doe'")).not_to_be_visible()

def test_view_contacts(browser):
    # AC007: View list of contacts
    test_user_login(browser)  # Ensure user is logged in
    expect(browser.locator(".contact-list")).to_be_visible()

def test_add_contact_invalid(browser):
    # AC008: Add a new contact with invalid details
    test_user_login(browser)  # Ensure user is logged in
    browser.click("text='Add Contact'")
    browser.fill("input[name='name']", "")
    browser.click("button[type='submit']")
    expect(browser.locator(".error-message")).to_have_text("Name is required")

def test_edit_contact_invalid(browser):
    # AC009: Edit an existing contact with invalid details
    test_user_login(browser)  # Ensure user is logged in
    browser.click("text='Edit' >> nth=0")
    browser.fill("input[name='name']", "")
    browser.click("button[type='submit']")
    expect(browser.locator(".error-message")).to_have_text("Name is required")

def test_data_persistence(browser):
    # AC010: Data Persistence after refresh
    test_user_login(browser)  # Ensure user is logged in
    browser.click("text='Add Contact'")
    browser.fill("input[name='name']", "Persistent Contact")
    browser.fill("input[name='phone']", "0987654321")
    browser.fill("input[name='email']", "persistent@example.com")
    browser.click("button[type='submit']")
    browser.reload()
    expect(browser.locator("text='Persistent Contact'")).to_be_visible()

def test_access_control(browser):
    # AC011: Access control for non-logged-in users
    browser.goto("https://thinking-tester-contact-list.herokuapp.com/contacts")
    expect(browser).to_have_url("https://thinking-tester-contact-list.herokuapp.com/login")