import httpx
from fastapi import HTTPException

from app.config import settings


class PowerDNSClient:
    """PowerDNS Authoritative Server API client."""

    def __init__(self):
        self.base_url = f"{settings.pdns_api_url}/api/v1/servers/{settings.pdns_server_id}"
        self.headers = {
            "X-API-Key": settings.pdns_api_key,
            "Content-Type": "application/json",
        }

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(headers=self.headers, timeout=30.0)

    async def _handle_response(self, response: httpx.Response):
        if response.status_code >= 400:
            try:
                detail = response.json()
            except Exception:
                detail = response.text
            raise HTTPException(status_code=response.status_code, detail=detail)
        if response.status_code == 204:
            return None
        if response.headers.get("content-type", "").startswith("application/json"):
            return response.json()
        return response.text

    # ── Zone operations ──

    async def list_zones(self):
        async with self._client() as client:
            resp = await client.get(f"{self.base_url}/zones")
            return await self._handle_response(resp)

    async def get_zone(self, zone_id: str):
        async with self._client() as client:
            resp = await client.get(f"{self.base_url}/zones/{zone_id}")
            return await self._handle_response(resp)

    async def create_zone(self, data: dict):
        async with self._client() as client:
            resp = await client.post(f"{self.base_url}/zones", json=data)
            return await self._handle_response(resp)

    async def update_zone(self, zone_id: str, data: dict):
        async with self._client() as client:
            resp = await client.put(f"{self.base_url}/zones/{zone_id}", json=data)
            return await self._handle_response(resp)

    async def delete_zone(self, zone_id: str):
        async with self._client() as client:
            resp = await client.delete(f"{self.base_url}/zones/{zone_id}")
            return await self._handle_response(resp)

    # ── Record operations ──

    async def update_records(self, zone_id: str, rrsets: list[dict]):
        """PATCH zone to add/modify/delete records via rrsets."""
        payload = {"rrsets": rrsets}
        async with self._client() as client:
            resp = await client.patch(f"{self.base_url}/zones/{zone_id}", json=payload)
            return await self._handle_response(resp)

    # ── Server info ──

    async def get_server_info(self):
        async with self._client() as client:
            url = f"{settings.pdns_api_url}/api/v1/servers/{settings.pdns_server_id}"
            resp = await client.get(url)
            return await self._handle_response(resp)

    async def search(self, query: str, max_results: int = 100, object_type: str = "all"):
        async with self._client() as client:
            params = {"q": query, "max": max_results, "object_type": object_type}
            resp = await client.get(f"{self.base_url}/search-data", params=params)
            return await self._handle_response(resp)


pdns_client = PowerDNSClient()
