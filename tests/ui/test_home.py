from playwright.sync_api import expect


def test_home_page_shows_products(page):
    page.goto("/")

    names = page.locator('[data-test="product-name"]')
    expect(names).not_to_have_count(0)
    expect(names.first).to_be_visible()


def test_search_shows_only_matching_products(page, api_client):
    term = api_client.get("/products").json()["data"][0]["name"].split()[-1].lower()
    expected = api_client.get("/products/search", params={"q": term}).json()["data"]
    page.goto("/")

    page.locator('[data-test="search-query"]').fill(term)
    page.locator('[data-test="search-submit"]').click()

    expect(page.locator('[data-test="search-term"]')).to_have_text(term)
    names = page.locator('[data-test="product-name"]')
    expect(names).to_have_count(len(expected))  # waits until the list shows the search results
    for name in names.all():
        expect(name).to_contain_text(term, ignore_case=True)
