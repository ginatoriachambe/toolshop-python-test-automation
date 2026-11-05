import os

import requests

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8091")


def test_get_products_returns_non_empty_list():
    response = requests.get(f"{BASE_URL}/products", timeout=10)

    assert response.status_code == 200
    products = response.json()["data"]
    assert isinstance(products, list)
    assert len(products) > 0
