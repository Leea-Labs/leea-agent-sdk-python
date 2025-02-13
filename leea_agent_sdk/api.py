from os import getenv

import certifi
import urllib3


class LeeaApi:
    def __init__(self, api_key=None):
        self._api_host = getenv('LEEA_API_HOST', 'https://api.leealabs.com')
        self._api_key = api_key or getenv("LEEA_API_KEY")
        if not self._api_key:
            raise RuntimeError("Please provide LEEA_API_KEY")

        self._client = urllib3.PoolManager(
            cert_reqs='CERT_REQUIRED',
            ca_certs=certifi.where(),
            retries=urllib3.Retry(connect=5, read=5, redirect=5, backoff_factor=0.5),

        )

    def _request(self, endpoint, method='GET'):
        return self._client.request(method, f"{self._api_host}/{endpoint}", headers={"Authorization": f"Bearer {self._api_key}"}).json()

    def list_agents(self):
        return self._request('agents')

    def get_agent(self, alias):
        return self._request(f'agent/{alias}')
