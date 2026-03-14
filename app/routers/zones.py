from fastapi import APIRouter, status

from app.schemas.zone import ZoneCreate, ZoneUpdate
from app.services.pdns_client import pdns_client

router = APIRouter(prefix="/zones", tags=["Zones"])


@router.get("", summary="Zone 목록 조회")
async def list_zones():
    """모든 Zone 목록을 반환합니다."""
    return await pdns_client.list_zones()


@router.get("/{zone_id}", summary="Zone 상세 조회")
async def get_zone(zone_id: str):
    """특정 Zone의 상세 정보(레코드 포함)를 반환합니다."""
    return await pdns_client.get_zone(zone_id)


@router.post("", status_code=status.HTTP_201_CREATED, summary="Zone 생성")
async def create_zone(zone: ZoneCreate):
    """새 Zone을 생성합니다."""
    payload = {
        "name": zone.name,
        "kind": zone.kind,
        "nameservers": zone.nameservers,
        "soa_edit_api": zone.soa_edit_api,
    }
    if zone.masters:
        payload["masters"] = zone.masters
    return await pdns_client.create_zone(payload)


@router.put("/{zone_id}", summary="Zone 수정")
async def update_zone(zone_id: str, zone: ZoneUpdate):
    """Zone 설정을 수정합니다."""
    payload = zone.model_dump(exclude_none=True)
    return await pdns_client.update_zone(zone_id, payload)


@router.delete("/{zone_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Zone 삭제")
async def delete_zone(zone_id: str):
    """Zone을 삭제합니다."""
    await pdns_client.delete_zone(zone_id)


@router.put("/{zone_id}/axfr-retrieve", summary="Slave Zone AXFR 갱신")
async def axfr_retrieve(zone_id: str):
    """Slave Zone의 AXFR 전송을 트리거합니다."""
    return await pdns_client.update_zone(zone_id, {})


@router.put("/{zone_id}/notify", summary="Zone Notify 전송")
async def notify_zone(zone_id: str):
    """Zone의 Slave 서버들에게 NOTIFY를 전송합니다."""
    return await pdns_client.update_zone(zone_id, {})


@router.get("/{zone_id}/export", summary="Zone Export (AXFR 형식)")
async def export_zone(zone_id: str):
    """Zone 데이터를 AXFR 형식으로 내보냅니다."""
    return await pdns_client.get_zone(zone_id)
