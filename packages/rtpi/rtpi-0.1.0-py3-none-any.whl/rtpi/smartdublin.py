from typing import Optional
from urllib.parse import urljoin

import httpx


def is_async(func):
    def wrapper(self, *args, is_async=False, **kwargs):
        self.async_client = is_async
        return func(self, *args, **kwargs)

    return wrapper


class SmartDublinAPI:
    ENDPOINT = "https://data.smartdublin.ie/cgi-bin/rtpi/realtimebusinformation"

    def __init__(self, async_client=False):
        self._async_client = async_client

    async def _async_request(self, url, query):
        async with httpx.AsyncClient() as client:
            response = await client.get(self.ENDPOINT, params=query)
            return response.json()

    def _request(self, url, query):
        url = urljoin(self.ENDPOINT, url)

        if self._async_client:
            return self._async_request(url, query)

        return httpx.get(url, params=query).json()

    @is_async
    def realtime_bus_information(
        self,
        stopid: int,
        routeid: Optional[str] = None,
        operator: Optional[str] = None,
        maxresults: Optional[int] = None,
    ) -> dict:
        """Real time bus information for a given stop number and route"""
        query = {
            "stopid": stopid,
            "routeid": routeid,
            "operator": operator,
        }

        if maxresults:
            query["maxresults"] = maxresults

        return self._request("realtimebusinformation", query)
