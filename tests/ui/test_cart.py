from playwright.sync_api import expect


def test_add_to_cart_updates_cart_indicator(page, product_id):
    page.goto(f"/product/{product_id}")
    expect(page.locator('[data-test="product-name"]')).to_be_visible()  # page has rendered
    cart_quantity = page.locator('[data-test="cart-quantity"]')
    expect(cart_quantity).to_have_count(0)  # new browser context starts with an empty cart

    page.locator('[data-test="add-to-cart"]').click()

    expect(cart_quantity).to_have_text("1")
