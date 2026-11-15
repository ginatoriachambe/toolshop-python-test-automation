NON_EXISTENT_ID = "01AAAAAAAAAAAAAAAAAAAAAAAA"  # valid ULID format, no such product


def get_first_product(api_client):
    return api_client.get("/products").json()["data"][0]


def test_get_products_returns_paginated_list(api_client):
    response = api_client.get("/products")

    assert response.status_code == 200
    body = response.json()
    assert body["current_page"] == 1
    assert len(body["data"]) > 0
    assert len(body["data"]) <= body["per_page"]
    assert body["total"] >= len(body["data"])


def test_get_product_by_id_returns_that_product(api_client):
    product = get_first_product(api_client)

    response = api_client.get(f"/products/{product['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == product["id"]
    assert response.json()["name"] == product["name"]


def test_get_product_with_unknown_id_returns_404(api_client):
    response = api_client.get(f"/products/{NON_EXISTENT_ID}")

    assert response.status_code == 404
    assert response.json() == {"message": "Requested item not found"}


def test_search_returns_only_matching_products(api_client):
    term = get_first_product(api_client)["name"].split()[-1].lower()

    response = api_client.get("/products/search", params={"q": term})

    assert response.status_code == 200
    products = response.json()["data"]
    assert len(products) > 0
    for product in products:
        assert term in product["name"].lower()
