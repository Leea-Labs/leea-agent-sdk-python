import json
from http import HTTPStatus
from os import getenv

import certifi
import urllib3


class LeeaApi:
    def __init__(self, api_key=None):
        self._api_host = getenv("LEEA_API_HOST", "https://api.leealabs.com")
        self._api_key = api_key or getenv("LEEA_API_KEY")
        if not self._api_key:
            raise RuntimeError("Please provide LEEA_API_KEY")

        self._client = urllib3.PoolManager(
            cert_reqs="CERT_REQUIRED",
            ca_certs=certifi.where(),
            retries=urllib3.Retry(connect=5, read=5, redirect=5, backoff_factor=0.5),
        )

    def _request(self, endpoint, method="GET"):
        url = f"{self._api_host}/{endpoint}"

        try:
            response = self._client.request(
                method, url, headers={"Authorization": f"Bearer {self._api_key}"}
            )
        except urllib3.exceptions.HTTPError as e:
            raise RuntimeError(f"HTTP request failed: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected error during request: {e}") from e

        if response.status != HTTPStatus.OK:
            try:
                error_message = response.data.decode()
            except Exception:
                error_message = "Failed to decode error message."
            raise RuntimeError(
                f"Request to {url} failed with status {response.status}: {error_message}"
            )

        if not response.data:
            raise RuntimeError("Empty response from API.")

        try:
            return response.json()
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to decode JSON response: {e}") from e

    def list_agents(self):
        return self._request("agents")

    def get_agent(self, alias):
        return self._request(f"agent/{alias}")
