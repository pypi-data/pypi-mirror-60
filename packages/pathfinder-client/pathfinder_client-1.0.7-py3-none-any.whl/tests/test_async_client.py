import pytest
from contextlib import ExitStack

from pathfinder_client.async_client import AsyncPathfinderClient
from pathfinder_client import constants
from pathfinder_client import exceptions


@pytest.mark.parametrize(
    ['api_key', 'exception'],
    [
        [
            'wrong_api_key',
            exceptions.PathfinderForbidden
        ],
        [
            'api_key',
            None
        ]
    ]
)
async def test_errors(api_key, exception):
    client = AsyncPathfinderClient('http://localhost:8080', api_key)
    with pytest.raises(exception) if exception else ExitStack():
        points = await client.route(
            [55.78881, 37.588005],
            [55.789447, 37.592318],
        )
        assert len(points) >= 2


@pytest.mark.parametrize(
    ['router'],
    [
        [
            constants.YANDEX_ROUTER
        ],
        [
            constants.HERE_ROUTER
        ],
        [
            constants.ATISU_ROUTER
        ]
    ]
)
async def test_routers(router):
    client = AsyncPathfinderClient('http://localhost:8080', 'api_key')
    points = await client.route(
        [55.78881, 37.588005],
        [55.789447, 37.592318],
        router=router
    )
    assert len(points) >= 2
