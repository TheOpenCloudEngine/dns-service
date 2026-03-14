import pytest

from tests.conftest import AUTH, ZONE_DETAIL_RESPONSE, ZONE_ID, ZONE_LIST_RESPONSE


@pytest.mark.anyio
async def test_list_zones(client, mock_pdns):
    """Zone 목록 조회 테스트"""
    resp = await client.get("/api/v1/zones", auth=AUTH)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == "dev.net."
    assert data[0]["kind"] == "Native"
    mock_pdns["zones"].list_zones.assert_called_once()


@pytest.mark.anyio
async def test_get_zone(client, mock_pdns):
    """Zone 상세 조회 테스트"""
    resp = await client.get(f"/api/v1/zones/{ZONE_ID}", auth=AUTH)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "dev.net."
    assert "rrsets" in data
    assert len(data["rrsets"]) == 5  # SOA, NS, www A, api A, mail MX
    mock_pdns["zones"].get_zone.assert_called_once_with(ZONE_ID)


@pytest.mark.anyio
async def test_create_zone(client, mock_pdns):
    """Zone 생성 테스트 - dev.net"""
    payload = {
        "name": "dev.net.",
        "kind": "Native",
        "nameservers": ["ns1.dev.net.", "ns2.dev.net."],
    }
    resp = await client.post("/api/v1/zones", json=payload, auth=AUTH)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "dev.net."

    call_args = mock_pdns["zones"].create_zone.call_args[0][0]
    assert call_args["name"] == "dev.net."
    assert call_args["kind"] == "Native"
    assert "ns1.dev.net." in call_args["nameservers"]


@pytest.mark.anyio
async def test_create_zone_master(client, mock_pdns):
    """Master Zone 생성 테스트"""
    payload = {
        "name": "dev.net.",
        "kind": "Master",
        "nameservers": ["ns1.dev.net."],
        "soa_edit_api": "EPOCH",
    }
    resp = await client.post("/api/v1/zones", json=payload, auth=AUTH)
    assert resp.status_code == 201

    call_args = mock_pdns["zones"].create_zone.call_args[0][0]
    assert call_args["kind"] == "Master"
    assert call_args["soa_edit_api"] == "EPOCH"


@pytest.mark.anyio
async def test_create_zone_slave(client, mock_pdns):
    """Slave Zone 생성 테스트"""
    payload = {
        "name": "dev.net.",
        "kind": "Slave",
        "masters": ["192.168.1.1"],
    }
    resp = await client.post("/api/v1/zones", json=payload, auth=AUTH)
    assert resp.status_code == 201

    call_args = mock_pdns["zones"].create_zone.call_args[0][0]
    assert call_args["kind"] == "Slave"
    assert "192.168.1.1" in call_args["masters"]


@pytest.mark.anyio
async def test_update_zone(client, mock_pdns):
    """Zone 수정 테스트"""
    payload = {"kind": "Master"}
    resp = await client.put(f"/api/v1/zones/{ZONE_ID}", json=payload, auth=AUTH)
    assert resp.status_code == 200
    mock_pdns["zones"].update_zone.assert_called_once_with(ZONE_ID, {"kind": "Master"})


@pytest.mark.anyio
async def test_update_zone_partial(client, mock_pdns):
    """Zone 부분 수정 테스트 - None 필드는 제외"""
    payload = {"kind": "Master", "account": "ops-team"}
    resp = await client.put(f"/api/v1/zones/{ZONE_ID}", json=payload, auth=AUTH)
    assert resp.status_code == 200

    call_args = mock_pdns["zones"].update_zone.call_args[0][1]
    assert call_args["kind"] == "Master"
    assert call_args["account"] == "ops-team"
    assert "masters" not in call_args  # None 필드 제외 확인


@pytest.mark.anyio
async def test_delete_zone(client, mock_pdns):
    """Zone 삭제 테스트"""
    resp = await client.delete(f"/api/v1/zones/{ZONE_ID}", auth=AUTH)
    assert resp.status_code == 204
    mock_pdns["zones"].delete_zone.assert_called_once_with(ZONE_ID)


@pytest.mark.anyio
async def test_export_zone(client, mock_pdns):
    """Zone Export 테스트"""
    resp = await client.get(f"/api/v1/zones/{ZONE_ID}/export", auth=AUTH)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "dev.net."
    assert "rrsets" in data


@pytest.mark.anyio
async def test_create_zone_missing_name(client, mock_pdns):
    """Zone 생성 시 name 필드 누락 → 422"""
    payload = {"kind": "Native"}
    resp = await client.post("/api/v1/zones", json=payload, auth=AUTH)
    assert resp.status_code == 422
