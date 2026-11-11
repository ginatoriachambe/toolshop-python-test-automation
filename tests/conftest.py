import os

import pytest

from toolshop.api_client import ApiClient

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8091")


@pytest.fixture(scope="session")
def api_client():
    client = ApiClient(BASE_URL)
    yield client
    client.close()
