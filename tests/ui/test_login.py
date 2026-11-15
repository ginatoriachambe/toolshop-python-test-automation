import re

from playwright.sync_api import expect


def test_registered_user_can_log_in(page, registered_user):
    page.goto("/auth/login")

    page.locator('[data-test="email"]').fill(registered_user["email"])
    page.locator('[data-test="password"]').fill(registered_user["password"])
    page.locator('[data-test="login-submit"]').click()

    expect(page).to_have_url(re.compile(r"/account$"))
    expect(page.locator('[data-test="page-title"]')).to_have_text("My account")
    expect(page.locator('[data-test="nav-menu"]')).to_contain_text(registered_user["first_name"])
