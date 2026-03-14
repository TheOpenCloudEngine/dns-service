import pytest

from tests.conftest import AUTH, BASE_URL


@pytest.mark.anyio
async def test_auth_required(client, mock_pdns):
    """인증 없이 API 호출 시 401 반환"""
    resp = await client.get("/api/v1/zones")
    assert resp.status_code == 401


@pytest.mark.anyio
async def test_auth_wrong_password(client, mock_pdns):
    """잘못된 비밀번호로 API 호출 시 401 반환"""
    resp = await client.get("/api/v1/zones", auth=("admin", "wrong"))
    assert resp.status_code == 401


@pytest.mark.anyio
async def test_auth_wrong_username(client, mock_pdns):
    """잘못된 사용자명으로 API 호출 시 401 반환"""
    resp = await client.get("/api/v1/zones", auth=("wrong", "admin"))
    assert resp.status_code == 401


@pytest.mark.anyio
async def test_auth_success(client, mock_pdns):
    """올바른 인증 정보로 API 호출 성공"""
    resp = await client.get("/api/v1/zones", auth=AUTH)
    assert resp.status_code == 200
