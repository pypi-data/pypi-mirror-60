import requests

from pathfinder_client import base_client
from pathfinder_client import constants


class SyncPathfinderClient(base_client.BasePathfinderClient):
    def __init__(self, base_url, api_key):
        super().__init__(base_url, api_key)
        self.request_maker = requests

    def route(self, *points, router=constants.HERE_ROUTER):
        response = self._make_route_request(points, router)
        return self._handle_status_and_get_response_body(response)

    def geocode(self, address):
        response = self._make_geocode_request(address)
        return self._handle_status_and_get_response_body(response)

    @staticmethod
    def _get_status(response):
        return response.status_code
