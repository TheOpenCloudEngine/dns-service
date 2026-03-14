import pytest

from tests.conftest import AUTH, BASE_URL


@pytest.mark.anyio
async def test_root(client):
    """루트 엔드포인트 테스트"""
    resp = await client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["service"] == "DNS Service API"
    assert data["status"] == "running"


@pytest.mark.anyio
async def test_health(client):
    """헬스 체크 엔드포인트 테스트"""
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


@pytest.mark.anyio
async def test_swagger_docs(client):
    """Swagger UI 접근 테스트"""
    resp = await client.get("/docs")
    assert resp.status_code == 200
    assert "swagger" in resp.text.lower() or "openapi" in resp.text.lower()


@pytest.mark.anyio
async def test_openapi_schema(client):
    """OpenAPI 스키마 정상 반환 테스트"""
    resp = await client.get("/openapi.json")
    assert resp.status_code == 200
    schema = resp.json()
    assert schema["info"]["title"] == "DNS Service API"
    assert "paths" in schema
    # Zone 및 Record 엔드포인트 존재 확인
    assert "/api/v1/zones" in schema["paths"]
    assert "/api/v1/zones/{zone_id}/records" in schema["paths"]
