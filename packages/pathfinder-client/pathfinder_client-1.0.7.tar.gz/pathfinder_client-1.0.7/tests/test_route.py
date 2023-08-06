import contextlib
import typing
import pytest

from pathfinder_client.base_client import BasePathfinderClient
from pathfinder_client.async_client import AsyncPathfinderClient
from pathfinder_client.sync_client import SyncPathfinderClient
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
    with pytest.raises(exception) if exception else contextlib.ExitStack():
        result = await client.route(
            [55.78881, 37.588005],
            [55.789447, 37.592318],
        )
        assert len(result['points']) >= 2


@pytest.mark.parametrize(
    ['client_class'],
    [
        [
            AsyncPathfinderClient
        ],
        [
            SyncPathfinderClient
        ]
    ]
)
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
        ],
        [
            None
        ]
    ]
)
async def test_route(router, client_class: typing.Type[BasePathfinderClient]):
    client = client_class('http://localhost:8080', 'api_key')
    result = client.route(
        [55.78881, 37.588005],
        [55.789447, 37.592318],
        router=router
    )
    if client_class is AsyncPathfinderClient:
        result = await result
    assert len(result['points']) >= 2
