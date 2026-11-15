import os
import uuid

import pytest

from toolshop.api_client import ApiClient

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8091")
TEST_PASSWORD = "Xq7#mT2!vLp9"  # meets the API rules and is not in a known data leak


@pytest.fixture(scope="session")
def api_base_url():
    return BASE_URL


@pytest.fixture(scope="session")
def api_client(api_base_url):
    client = ApiClient(api_base_url)
    yield client
    client.close()


@pytest.fixture
def user_payload():
    return {
        "first_name": "Test",
        "last_name": "User",
        "email": f"test-{uuid.uuid4().hex}@example.com",
        "password": TEST_PASSWORD,
    }


@pytest.fixture
def registered_user(api_client, user_payload):
    response = api_client.post("/users/register", json=user_payload)
    assert response.status_code == 201, response.text
    return user_payload


@pytest.fixture
def auth_token(api_client, registered_user):
    response = api_client.login(registered_user["email"], registered_user["password"])
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


@pytest.fixture
def cart_id(api_client):
    response = api_client.post("/carts")
    assert response.status_code == 201, response.text
    return response.json()["id"]


@pytest.fixture
def product_id(api_client):
    products = api_client.get("/products").json()["data"]
    for product in products:
        if product["in_stock"] and not product["is_rental"]:
            return product["id"]
    pytest.fail("No in-stock, non-rental product on the first page of /products")
