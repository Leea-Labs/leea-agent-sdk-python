import ssl
from os import getenv

import aiohttp
import certifi


class LeeaApi:
    def __init__(self, api_key=None):
        self._api_host = getenv("LEEA_API_HOST", "https://api.leealabs.com")
        self._api_key = api_key or getenv("LEEA_API_KEY")
        if not self._api_key:
            raise RuntimeError("Please provide LEEA_API_KEY")

        ssl_context = ssl.create_default_context(cafile=certifi.where())
        self._client = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context))

    async def _request(self, endpoint, method="GET"):
        url = f"{self._api_host}/{endpoint}"
        headers = {"Authorization": f"Bearer {self._api_key}"}

        try:
            async with self._client.request(method, url, headers=headers) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientResponseError as e:
            raise RuntimeError(f"HTTP error during API request to {url}: {e.status} - {e.message}")
        except Exception as e:
            raise RuntimeError(f"Error during API request to {url}: {e}")

    async def list_agents(self):
        return await self._request("agents")

    async def get_agent(self, alias):
        return await self._request(f"agent/{alias}")

    async def close_session(self):
        await self._client.close()
