import pytest

from tests.conftest import AUTH


@pytest.mark.anyio
async def test_server_info(client, mock_pdns):
    """PowerDNS 서버 정보 조회 테스트"""
    resp = await client.get("/api/v1/server", auth=AUTH)
    assert resp.status_code == 200
    data = resp.json()
    assert data["daemon_type"] == "authoritative"
    assert data["version"] == "4.4.1"
    mock_pdns["main"].get_server_info.assert_called_once()


@pytest.mark.anyio
async def test_search(client, mock_pdns):
    """DNS 검색 테스트"""
    resp = await client.get("/api/v1/search", params={"q": "www"}, auth=AUTH)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == "www.dev.net."
    mock_pdns["main"].search.assert_called_once_with("www", 100, "all")


@pytest.mark.anyio
async def test_search_with_params(client, mock_pdns):
    """검색 파라미터 전달 테스트"""
    resp = await client.get(
        "/api/v1/search",
        params={"q": "dev", "max": 10, "object_type": "record"},
        auth=AUTH,
    )
    assert resp.status_code == 200
    mock_pdns["main"].search.assert_called_once_with("dev", 10, "record")


@pytest.mark.anyio
async def test_search_requires_query(client, mock_pdns):
    """검색어 누락 시 422"""
    resp = await client.get("/api/v1/search", auth=AUTH)
    assert resp.status_code == 422
