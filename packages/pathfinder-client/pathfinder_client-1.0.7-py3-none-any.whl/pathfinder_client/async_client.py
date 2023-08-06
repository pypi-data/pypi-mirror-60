import asyncio
import aiohttp

from pathfinder_client import base_client
from pathfinder_client import constants


class AsyncPathfinderClient(base_client.BasePathfinderClient):
    def __init__(self, base_url, api_key):
        super().__init__(base_url, api_key)
        self.request_maker = aiohttp.ClientSession()

    async def route(self, *points, router=constants.HERE_ROUTER):
        response = await self._make_route_request(points, router)
        return await self._handle_status_and_get_response_body(response)

    async def geocode(self, address):
        response = await self._make_geocode_request(address)
        return await self._handle_status_and_get_response_body(response)

    @staticmethod
    def _get_status(response):
        return response.status

    def __del__(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.request_maker.close())
