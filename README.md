# Toolshop Python Test Automation

API tests for the Toolshop app, written with pytest and requests.

## Layout

- `toolshop/` holds the API client (`ApiClient`).
- `tests/` holds the tests and fixtures (`conftest.py`).

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
