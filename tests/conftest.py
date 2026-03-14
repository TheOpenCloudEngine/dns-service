from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app

BASE_URL = "http://test"
AUTH = ("admin", "admin")

ZONE_ID = "dev.net."

ZONE_LIST_RESPONSE = [
    {
        "id": "dev.net.",
        "name": "dev.net.",
        "kind": "Native",
        "serial": 2024010101,
        "notified_serial": 0,
        "account": "",
        "dnssec": False,
    }
]

ZONE_DETAIL_RESPONSE = {
    "id": "dev.net.",
    "name": "dev.net.",
    "kind": "Native",
    "serial": 2024010101,
    "notified_serial": 0,
    "account": "",
    "dnssec": False,
    "rrsets": [
        {
            "name": "dev.net.",
            "type": "SOA",
            "ttl": 3600,
            "records": [
                {
                    "content": "ns1.dev.net. admin.dev.net. 2024010101 10800 3600 604800 3600",
                    "disabled": False,
                }
            ],
            "comments": [],
        },
        {
            "name": "dev.net.",
            "type": "NS",
            "ttl": 3600,
            "records": [
                {"content": "ns1.dev.net.", "disabled": False},
                {"content": "ns2.dev.net.", "disabled": False},
            ],
            "comments": [],
        },
        {
            "name": "www.dev.net.",
            "type": "A",
            "ttl": 3600,
            "records": [{"content": "10.0.0.1", "disabled": False}],
            "comments": [],
        },
        {
            "name": "api.dev.net.",
            "type": "A",
            "ttl": 3600,
            "records": [{"content": "10.0.0.2", "disabled": False}],
            "comments": [],
        },
        {
            "name": "mail.dev.net.",
            "type": "MX",
            "ttl": 3600,
            "records": [{"content": "10 mail.dev.net.", "disabled": False}],
            "comments": [],
        },
    ],
}

SERVER_INFO_RESPONSE = {
    "type": "Server",
    "id": "localhost",
    "daemon_type": "authoritative",
    "version": "4.4.1",
    "url": "/api/v1/servers/localhost",
}

SEARCH_RESPONSE = [
    {
        "content": "10.0.0.1",
        "disabled": False,
        "name": "www.dev.net.",
        "object_type": "record",
        "ttl": 3600,
        "type": "A",
        "zone": "dev.net.",
        "zone_id": "dev.net.",
    }
]


@pytest.fixture
def mock_pdns():
    """PowerDNS API 클라이언트를 모킹합니다."""
    with patch("app.routers.zones.pdns_client") as mock_zones, \
         patch("app.routers.records.pdns_client") as mock_records, \
         patch("app.main.pdns_client") as mock_main:
        # Zone operations
        mock_zones.list_zones = AsyncMock(return_value=ZONE_LIST_RESPONSE)
        mock_zones.get_zone = AsyncMock(return_value=ZONE_DETAIL_RESPONSE)
        mock_zones.create_zone = AsyncMock(return_value=ZONE_DETAIL_RESPONSE)
        mock_zones.update_zone = AsyncMock(return_value=None)
        mock_zones.delete_zone = AsyncMock(return_value=None)

        # Record operations
        mock_records.get_zone = AsyncMock(return_value=ZONE_DETAIL_RESPONSE)
        mock_records.update_records = AsyncMock(return_value=None)

        # Main operations
        mock_main.get_server_info = AsyncMock(return_value=SERVER_INFO_RESPONSE)
        mock_main.search = AsyncMock(return_value=SEARCH_RESPONSE)

        yield {
            "zones": mock_zones,
            "records": mock_records,
            "main": mock_main,
        }


@pytest.fixture
async def client():
    """비동기 테스트 클라이언트를 생성합니다."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        yield ac
