# Toolshop Python Test Automation

API and UI tests for the Toolshop app, written with pytest, requests and Playwright.

## Layout

- `toolshop/` holds the API client (`ApiClient`).
- `tests/conftest.py` holds the fixtures shared by API and UI tests.
- `tests/api/` holds the API tests.
- `tests/ui/` holds the UI tests and their `base_url` fixture (`conftest.py`).

## Setup

Requires Python 3.12 and pip 25.1 or newer.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install --group test
```

## Run

With the Toolshop app running locally:

```bash
pytest
```

The API base URL defaults to `http://localhost:8091`. To test another environment, set `API_BASE_URL`:

```bash
API_BASE_URL=http://other-host:8091 pytest
```

## Running the UI tests

The UI tests use Playwright. After `pip install --group test`, download the browser once:

```bash
playwright install chromium
```

Then, with the Toolshop UI running locally:

```bash
pytest tests/ui
```

They run headless in Chromium. The UI base URL defaults to `http://localhost:4200`. To test another environment, set `UI_BASE_URL`:

```bash
UI_BASE_URL=http://other-host:4200 pytest tests/ui
```

The UI tests also call the API (to register users and pick products), so `API_BASE_URL` must point at the same environment.
