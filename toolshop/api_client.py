import requests


def _auth_headers(token):
    return {"Authorization": f"Bearer {token}"} if token else {}


class ApiClient:
    def __init__(self, base_url, timeout=10):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()

    def get(self, path, params=None, token=None):
        return self.session.get(
            f"{self.base_url}{path}",
            params=params,
            headers=_auth_headers(token),
            timeout=self.timeout,
        )

    def post(self, path, json=None, token=None):
        return self.session.post(
            f"{self.base_url}{path}",
            json=json,
            headers=_auth_headers(token),
            timeout=self.timeout,
        )

    def login(self, email, password):
        return self.post("/users/login", json={"email": email, "password": password})

    def close(self):
        self.session.close()
