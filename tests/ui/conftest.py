import os

import pytest


# Overrides pytest-playwright's base_url, so page.goto("/") opens the UI, never the API.
@pytest.fixture(scope="session")
def base_url():
    return os.getenv("UI_BASE_URL", "http://localhost:4200")
