import pytest
from unittest.mock import AsyncMock

from tests.conftest import AUTH, ZONE_DETAIL_RESPONSE, ZONE_ID


# ── 레코드 조회 ──


@pytest.mark.anyio
async def test_list_records(client, mock_pdns):
    """dev.net. Zone의 전체 레코드 목록 조회"""
    resp = await client.get(f"/api/v1/zones/{ZONE_ID}/records", auth=AUTH)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 5  # SOA, NS, www A, api A, mail MX


@pytest.mark.anyio
async def test_list_records_filter_by_type(client, mock_pdns):
    """레코드 타입(A)으로 필터링 조회"""
    resp = await client.get(
        f"/api/v1/zones/{ZONE_ID}/records", params={"record_type": "A"}, auth=AUTH
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2  # www.dev.net. A, api.dev.net. A
    for record in data:
        assert record["type"] == "A"


@pytest.mark.anyio
async def test_list_records_filter_mx(client, mock_pdns):
    """레코드 타입(MX)으로 필터링 조회"""
    resp = await client.get(
        f"/api/v1/zones/{ZONE_ID}/records", params={"record_type": "MX"}, auth=AUTH
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "mail.dev.net."


@pytest.mark.anyio
async def test_list_records_filter_no_match(client, mock_pdns):
    """존재하지 않는 레코드 타입 필터링 → 빈 배열"""
    resp = await client.get(
        f"/api/v1/zones/{ZONE_ID}/records", params={"record_type": "AAAA"}, auth=AUTH
    )
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.anyio
async def test_get_record(client, mock_pdns):
    """특정 레코드 조회 - www.dev.net. A"""
    resp = await client.get(
        f"/api/v1/zones/{ZONE_ID}/records/www.dev.net./A", auth=AUTH
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "www.dev.net."
    assert data["type"] == "A"
    assert data["records"][0]["content"] == "10.0.0.1"


@pytest.mark.anyio
async def test_get_record_not_found(client, mock_pdns):
    """존재하지 않는 레코드 조회 → 404"""
    resp = await client.get(
        f"/api/v1/zones/{ZONE_ID}/records/unknown.dev.net./A", auth=AUTH
    )
    assert resp.status_code == 404


# ── 레코드 생성 ──


@pytest.mark.anyio
async def test_create_a_record(client, mock_pdns):
    """A 레코드 생성 - web.dev.net."""
    payload = {
        "name": "web.dev.net.",
        "type": "A",
        "ttl": 3600,
        "records": [{"content": "10.0.0.10", "disabled": False}],
    }
    resp = await client.post(f"/api/v1/zones/{ZONE_ID}/records", json=payload, auth=AUTH)
    assert resp.status_code == 201
    data = resp.json()
    assert data["message"] == "Record created"
    assert data["name"] == "web.dev.net."

    call_args = mock_pdns["records"].update_records.call_args
    rrsets = call_args[0][1]
    assert rrsets[0]["name"] == "web.dev.net."
    assert rrsets[0]["type"] == "A"
    assert rrsets[0]["changetype"] == "REPLACE"


@pytest.mark.anyio
async def test_create_aaaa_record(client, mock_pdns):
    """AAAA 레코드 생성"""
    payload = {
        "name": "ipv6.dev.net.",
        "type": "AAAA",
        "ttl": 3600,
        "records": [{"content": "2001:db8::1", "disabled": False}],
    }
    resp = await client.post(f"/api/v1/zones/{ZONE_ID}/records", json=payload, auth=AUTH)
    assert resp.status_code == 201
    assert resp.json()["type"] == "AAAA"


@pytest.mark.anyio
async def test_create_cname_record(client, mock_pdns):
    """CNAME 레코드 생성"""
    payload = {
        "name": "blog.dev.net.",
        "type": "CNAME",
        "ttl": 3600,
        "records": [{"content": "www.dev.net.", "disabled": False}],
    }
    resp = await client.post(f"/api/v1/zones/{ZONE_ID}/records", json=payload, auth=AUTH)
    assert resp.status_code == 201

    rrsets = mock_pdns["records"].update_records.call_args[0][1]
    assert rrsets[0]["type"] == "CNAME"
    assert rrsets[0]["records"][0]["content"] == "www.dev.net."


@pytest.mark.anyio
async def test_create_mx_record(client, mock_pdns):
    """MX 레코드 생성"""
    payload = {
        "name": "dev.net.",
        "type": "MX",
        "ttl": 3600,
        "records": [
            {"content": "10 mail1.dev.net.", "disabled": False},
            {"content": "20 mail2.dev.net.", "disabled": False},
        ],
    }
    resp = await client.post(f"/api/v1/zones/{ZONE_ID}/records", json=payload, auth=AUTH)
    assert resp.status_code == 201

    rrsets = mock_pdns["records"].update_records.call_args[0][1]
    assert len(rrsets[0]["records"]) == 2


@pytest.mark.anyio
async def test_create_txt_record(client, mock_pdns):
    """TXT 레코드 생성 (SPF 등)"""
    payload = {
        "name": "dev.net.",
        "type": "TXT",
        "ttl": 3600,
        "records": [{"content": '"v=spf1 mx -all"', "disabled": False}],
    }
    resp = await client.post(f"/api/v1/zones/{ZONE_ID}/records", json=payload, auth=AUTH)
    assert resp.status_code == 201
    assert resp.json()["type"] == "TXT"


@pytest.mark.anyio
async def test_create_srv_record(client, mock_pdns):
    """SRV 레코드 생성"""
    payload = {
        "name": "_sip._tcp.dev.net.",
        "type": "SRV",
        "ttl": 3600,
        "records": [{"content": "10 60 5060 sip.dev.net.", "disabled": False}],
    }
    resp = await client.post(f"/api/v1/zones/{ZONE_ID}/records", json=payload, auth=AUTH)
    assert resp.status_code == 201
    assert resp.json()["type"] == "SRV"


@pytest.mark.anyio
async def test_create_ns_record(client, mock_pdns):
    """NS 레코드 생성"""
    payload = {
        "name": "sub.dev.net.",
        "type": "NS",
        "ttl": 3600,
        "records": [{"content": "ns1.sub.dev.net.", "disabled": False}],
    }
    resp = await client.post(f"/api/v1/zones/{ZONE_ID}/records", json=payload, auth=AUTH)
    assert resp.status_code == 201


@pytest.mark.anyio
async def test_create_record_multiple_values(client, mock_pdns):
    """하나의 A 레코드에 여러 IP 설정 (라운드 로빈)"""
    payload = {
        "name": "lb.dev.net.",
        "type": "A",
        "ttl": 300,
        "records": [
            {"content": "10.0.0.11", "disabled": False},
            {"content": "10.0.0.12", "disabled": False},
            {"content": "10.0.0.13", "disabled": False},
        ],
    }
    resp = await client.post(f"/api/v1/zones/{ZONE_ID}/records", json=payload, auth=AUTH)
    assert resp.status_code == 201

    rrsets = mock_pdns["records"].update_records.call_args[0][1]
    assert len(rrsets[0]["records"]) == 3


@pytest.mark.anyio
async def test_create_record_custom_ttl(client, mock_pdns):
    """TTL 커스텀 설정 테스트"""
    payload = {
        "name": "short.dev.net.",
        "type": "A",
        "ttl": 60,
        "records": [{"content": "10.0.0.99", "disabled": False}],
    }
    resp = await client.post(f"/api/v1/zones/{ZONE_ID}/records", json=payload, auth=AUTH)
    assert resp.status_code == 201

    rrsets = mock_pdns["records"].update_records.call_args[0][1]
    assert rrsets[0]["ttl"] == 60


# ── 레코드 수정 ──


@pytest.mark.anyio
async def test_update_record(client, mock_pdns):
    """레코드 수정 - www.dev.net. A 레코드 IP 변경"""
    payload = {
        "name": "www.dev.net.",
        "type": "A",
        "ttl": 7200,
        "records": [
            {"content": "10.0.0.100", "disabled": False},
            {"content": "10.0.0.101", "disabled": False},
        ],
    }
    resp = await client.put(f"/api/v1/zones/{ZONE_ID}/records", json=payload, auth=AUTH)
    assert resp.status_code == 200
    data = resp.json()
    assert data["message"] == "Record updated"

    rrsets = mock_pdns["records"].update_records.call_args[0][1]
    assert rrsets[0]["ttl"] == 7200
    assert len(rrsets[0]["records"]) == 2
    assert rrsets[0]["changetype"] == "REPLACE"


@pytest.mark.anyio
async def test_update_record_disable(client, mock_pdns):
    """레코드 비활성화 테스트"""
    payload = {
        "name": "api.dev.net.",
        "type": "A",
        "ttl": 3600,
        "records": [{"content": "10.0.0.2", "disabled": True}],
    }
    resp = await client.put(f"/api/v1/zones/{ZONE_ID}/records", json=payload, auth=AUTH)
    assert resp.status_code == 200

    rrsets = mock_pdns["records"].update_records.call_args[0][1]
    assert rrsets[0]["records"][0]["disabled"] is True


# ── 레코드 일괄 처리 ──


@pytest.mark.anyio
async def test_batch_create_records(client, mock_pdns):
    """여러 레코드 일괄 생성"""
    payload = [
        {
            "name": "app1.dev.net.",
            "type": "A",
            "ttl": 3600,
            "records": [{"content": "10.0.1.1", "disabled": False}],
        },
        {
            "name": "app2.dev.net.",
            "type": "A",
            "ttl": 3600,
            "records": [{"content": "10.0.1.2", "disabled": False}],
        },
        {
            "name": "app3.dev.net.",
            "type": "A",
            "ttl": 3600,
            "records": [{"content": "10.0.1.3", "disabled": False}],
        },
    ]
    resp = await client.post(
        f"/api/v1/zones/{ZONE_ID}/records/batch", json=payload, auth=AUTH
    )
    assert resp.status_code == 200
    assert resp.json()["message"] == "3 records updated"

    rrsets = mock_pdns["records"].update_records.call_args[0][1]
    assert len(rrsets) == 3
    names = [r["name"] for r in rrsets]
    assert "app1.dev.net." in names
    assert "app2.dev.net." in names
    assert "app3.dev.net." in names


@pytest.mark.anyio
async def test_batch_mixed_types(client, mock_pdns):
    """다양한 타입의 레코드 일괄 생성"""
    payload = [
        {
            "name": "db.dev.net.",
            "type": "A",
            "ttl": 3600,
            "records": [{"content": "10.0.2.1", "disabled": False}],
        },
        {
            "name": "db.dev.net.",
            "type": "AAAA",
            "ttl": 3600,
            "records": [{"content": "2001:db8::2", "disabled": False}],
        },
    ]
    resp = await client.post(
        f"/api/v1/zones/{ZONE_ID}/records/batch", json=payload, auth=AUTH
    )
    assert resp.status_code == 200
    assert resp.json()["message"] == "2 records updated"


# ── 레코드 삭제 ──


@pytest.mark.anyio
async def test_delete_record(client, mock_pdns):
    """레코드 삭제 - www.dev.net. A"""
    payload = {"name": "www.dev.net.", "type": "A"}
    resp = await client.request(
        "DELETE", f"/api/v1/zones/{ZONE_ID}/records", json=payload, auth=AUTH
    )
    assert resp.status_code == 204

    rrsets = mock_pdns["records"].update_records.call_args[0][1]
    assert rrsets[0]["name"] == "www.dev.net."
    assert rrsets[0]["type"] == "A"
    assert rrsets[0]["changetype"] == "DELETE"


@pytest.mark.anyio
async def test_delete_mx_record(client, mock_pdns):
    """MX 레코드 삭제"""
    payload = {"name": "mail.dev.net.", "type": "MX"}
    resp = await client.request(
        "DELETE", f"/api/v1/zones/{ZONE_ID}/records", json=payload, auth=AUTH
    )
    assert resp.status_code == 204

    rrsets = mock_pdns["records"].update_records.call_args[0][1]
    assert rrsets[0]["type"] == "MX"
    assert rrsets[0]["changetype"] == "DELETE"


# ── 유효성 검증 ──


@pytest.mark.anyio
async def test_create_record_missing_name(client, mock_pdns):
    """레코드 생성 시 name 누락 → 422"""
    payload = {
        "type": "A",
        "ttl": 3600,
        "records": [{"content": "10.0.0.1"}],
    }
    resp = await client.post(f"/api/v1/zones/{ZONE_ID}/records", json=payload, auth=AUTH)
    assert resp.status_code == 422


@pytest.mark.anyio
async def test_create_record_missing_records(client, mock_pdns):
    """레코드 생성 시 records 누락 → 422"""
    payload = {
        "name": "test.dev.net.",
        "type": "A",
        "ttl": 3600,
    }
    resp = await client.post(f"/api/v1/zones/{ZONE_ID}/records", json=payload, auth=AUTH)
    assert resp.status_code == 422


@pytest.mark.anyio
async def test_create_record_type_uppercase(client, mock_pdns):
    """소문자 타입 입력 시 자동 대문자 변환"""
    payload = {
        "name": "test.dev.net.",
        "type": "a",
        "ttl": 3600,
        "records": [{"content": "10.0.0.1", "disabled": False}],
    }
    resp = await client.post(f"/api/v1/zones/{ZONE_ID}/records", json=payload, auth=AUTH)
    assert resp.status_code == 201

    rrsets = mock_pdns["records"].update_records.call_args[0][1]
    assert rrsets[0]["type"] == "A"
