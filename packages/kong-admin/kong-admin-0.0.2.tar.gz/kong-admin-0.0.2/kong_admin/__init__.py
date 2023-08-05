"""
https://docs.konghq.com/1.4.x/admin-api/
"""

from urllib.parse import urljoin

import requests


class KongAdmin:
    def __init__(self, host):
        self.host = host

    def get_url(self, path: str) -> str:
        return urljoin(self.host, path)

    def request(self, method: str, path: str, json: dict = None) -> dict:
        url = self.get_url(path)
        return requests.request(method, url, json=json)

    def get(self, path: str, json: dict = None) -> dict:
        return self.request("get", path, json=json)

    def post(self, path: str, json: dict = None) -> dict:
        return self.request("post", path, json=json)

    def put(self, path: str, json: dict = None) -> dict:
        return self.request("put", path, json=json)

    def patch(self, path: str, json: dict = None) -> dict:
        return self.request("patch", path, json=json)

    def delete(self, path: str) -> dict:
        return self.request("delete", path)
