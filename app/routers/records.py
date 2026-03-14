from fastapi import APIRouter, status

from app.schemas.record import RecordCreate, RecordDelete, RecordUpdate
from app.services.pdns_client import pdns_client

router = APIRouter(prefix="/zones/{zone_id}/records", tags=["Records"])


@router.get("", summary="레코드 목록 조회")
async def list_records(zone_id: str, record_type: str | None = None):
    """Zone의 모든 DNS 레코드를 반환합니다. type 파라미터로 필터링 가능."""
    zone = await pdns_client.get_zone(zone_id)
    rrsets = zone.get("rrsets", [])
    if record_type:
        rrsets = [r for r in rrsets if r.get("type") == record_type.upper()]
    return rrsets


@router.get("/{record_name}/{record_type}", summary="특정 레코드 조회")
async def get_record(zone_id: str, record_name: str, record_type: str):
    """특정 이름과 타입의 DNS 레코드를 조회합니다."""
    zone = await pdns_client.get_zone(zone_id)
    rrsets = zone.get("rrsets", [])
    for rrset in rrsets:
        if rrset.get("name") == record_name and rrset.get("type") == record_type.upper():
            return rrset
    return {"error": "Record not found"}, 404


@router.post("", status_code=status.HTTP_201_CREATED, summary="레코드 생성")
async def create_record(zone_id: str, record: RecordCreate):
    """새 DNS 레코드를 생성합니다."""
    rrset = {
        "name": record.name,
        "type": record.type.upper(),
        "ttl": record.ttl,
        "changetype": "REPLACE",
        "records": [r.model_dump() for r in record.records],
    }
    await pdns_client.update_records(zone_id, [rrset])
    return {"message": "Record created", "name": record.name, "type": record.type}


@router.put("", summary="레코드 수정")
async def update_record(zone_id: str, record: RecordUpdate):
    """기존 DNS 레코드를 수정합니다."""
    rrset = {
        "name": record.name,
        "type": record.type.upper(),
        "ttl": record.ttl,
        "changetype": "REPLACE",
        "records": [r.model_dump() for r in record.records],
    }
    await pdns_client.update_records(zone_id, [rrset])
    return {"message": "Record updated", "name": record.name, "type": record.type}


@router.post("/batch", summary="레코드 일괄 생성/수정")
async def batch_update_records(zone_id: str, records: list[RecordCreate]):
    """여러 DNS 레코드를 한번에 생성/수정합니다."""
    rrsets = []
    for record in records:
        rrsets.append({
            "name": record.name,
            "type": record.type.upper(),
            "ttl": record.ttl,
            "changetype": "REPLACE",
            "records": [r.model_dump() for r in record.records],
        })
    await pdns_client.update_records(zone_id, rrsets)
    return {"message": f"{len(records)} records updated"}


@router.delete("", status_code=status.HTTP_204_NO_CONTENT, summary="레코드 삭제")
async def delete_record(zone_id: str, record: RecordDelete):
    """DNS 레코드를 삭제합니다."""
    rrset = {
        "name": record.name,
        "type": record.type.upper(),
        "changetype": "DELETE",
    }
    await pdns_client.update_records(zone_id, [rrset])
