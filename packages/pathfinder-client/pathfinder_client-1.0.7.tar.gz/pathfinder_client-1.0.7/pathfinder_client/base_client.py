import abc
import typing

from pathfinder_client import exceptions


class BasePathfinderClient(abc.ABC):
    request_maker: ...

    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key

    @typing.overload
    @abc.abstractmethod
    async def route(self, *points, router):
        raise NotImplementedError

    @abc.abstractmethod
    def route(self, *points, router):
        raise NotImplementedError

    @typing.overload
    @abc.abstractmethod
    async def geocode(self, address):
        raise NotImplementedError

    @abc.abstractmethod
    def geocode(self, address):
        raise NotImplementedError

    def _make_route_request(self, points, router):
        params = {'router': router} if router else {}
        return self.request_maker.post(
            url=f'{self.base_url}/route',
            params=params,
            headers={
                'PATHFINDER_API_KEY': self.api_key
            },
            json={
                'points': points[0] if len(points) == 1 else list(points)
            },
        )

    def _make_geocode_request(self, address):
        return self.request_maker.post(
            url=f'{self.base_url}/geocode',
            headers={
                'PATHFINDER_API_KEY': self.api_key
            },
            json={
                'address': address
            },
        )

    @classmethod
    def _handle_status_and_get_response_body(cls, response):
        cls._handle_status(response)
        return response.json()

    @classmethod
    def _handle_status(cls, response):
        status = cls._get_status(response)
        if status == 200:
            return
        if status == 400:
            raise exceptions.PathfinderBadRequest
        if status == 401:
            raise exceptions.PathfinderUnauthorized
        if status == 403:
            raise exceptions.PathfinderForbidden
        raise exceptions.PathfinderException

    @staticmethod
    @abc.abstractmethod
    def _get_status(response):
        raise NotImplementedError
