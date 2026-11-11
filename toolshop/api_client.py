import requests


class ApiClient:
    def __init__(self, base_url, timeout=10):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()

    def get(self, path, params=None):
        return self.session.get(f"{self.base_url}{path}", params=params, timeout=self.timeout)

    def close(self):
        self.session.close()
