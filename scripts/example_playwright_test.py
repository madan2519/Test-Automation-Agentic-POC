import pytest
from playwright.sync_api import Page, expect

def test_login_flow(page: Page):
    """
    STORY: User Login
    AC: User should be able to login with valid credentials
    """
    page.goto("https://example.com/login")
    page.fill("#username", "testuser")
    page.fill("#password", "password123")
    page.click("#login-button")
    
    expect(page).to_have_url("https://example.com/dashboard")
    expect(page.locator("#welcome-message")).to_be_visible()
