import typing
import pytest

from pathfinder_client.base_client import BasePathfinderClient
from pathfinder_client.async_client import AsyncPathfinderClient
from pathfinder_client.sync_client import SyncPathfinderClient


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
    ['address', 'coordinates'],
    [
        [
            'Москва',
            [55.8, 37.6],
        ],
        [
            'Saint Petersburg',
            [59.9, 30.3]
        ],
    ]
)
async def test_route(address, coordinates, client_class: typing.Type[BasePathfinderClient]):
    client = client_class('http://localhost:8080', 'api_key')
    result = client.geocode(address)
    if client_class is AsyncPathfinderClient:
        result = await result
    assert [round(coord, 1) for coord in result['point']] == coordinates
