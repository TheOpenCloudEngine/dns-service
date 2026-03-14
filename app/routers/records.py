from fastapi import APIRouter, HTTPException, Path, Query, status

from app.schemas.record import (
    BatchRecordResponse,
    RecordCreate,
    RecordDelete,
    RecordResponse,
    RecordUpdate,
)
from app.schemas.zone import RRSet
from app.services.pdns_client import pdns_client

router = APIRouter(prefix="/zones/{zone_id}/records", tags=["Records"])


@router.get(
    "",
    summary="레코드 목록 조회",
    response_model=list[RRSet],
    response_description="DNS 레코드(RRSet) 목록",
)
async def list_records(
    zone_id: str = Path(..., description="Zone ID (예: example.com.)", example="example.com."),
    record_type: str | None = Query(
        None,
        description="레코드 타입으로 필터링 (A, AAAA, CNAME, MX, TXT, NS, SOA 등)",
        example="A",
    ),
):
    """
    Zone에 속한 모든 DNS 레코드(RRSet)를 반환합니다.

    - **record_type** 파라미터로 특정 타입의 레코드만 필터링할 수 있습니다.
    - 예: `?record_type=A` → A 레코드만 반환
    """
    zone = await pdns_client.get_zone(zone_id)
    rrsets = zone.get("rrsets", [])
    if record_type:
        rrsets = [r for r in rrsets if r.get("type") == record_type.upper()]
    return rrsets


@router.get(
    "/{record_name}/{record_type}",
    summary="특정 레코드 조회",
    response_model=RRSet,
    response_description="DNS 레코드 정보",
    responses={
        404: {"description": "레코드를 찾을 수 없음"},
    },
)
async def get_record(
    zone_id: str = Path(..., description="Zone ID", example="example.com."),
    record_name: str = Path(..., description="레코드 이름 (FQDN)", example="www.example.com."),
    record_type: str = Path(..., description="레코드 타입", example="A"),
):
    """
    특정 이름과 타입의 DNS 레코드를 조회합니다.

    - **record_name**: 레코드 이름 (FQDN, 끝에 `.` 포함)
    - **record_type**: 레코드 타입 (A, AAAA, CNAME 등)
    """
    zone = await pdns_client.get_zone(zone_id)
    rrsets = zone.get("rrsets", [])
    for rrset in rrsets:
        if rrset.get("name") == record_name and rrset.get("type") == record_type.upper():
            return rrset
    raise HTTPException(status_code=404, detail=f"Record {record_name} ({record_type}) not found")


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="레코드 생성",
    response_model=RecordResponse,
    response_description="생성 결과",
    responses={
        422: {"description": "유효하지 않은 요청 데이터"},
    },
)
async def create_record(
    record: RecordCreate,
    zone_id: str = Path(..., description="Zone ID", example="example.com."),
):
    """
    새 DNS 레코드를 생성합니다.

    - **name**: 레코드 이름 (FQDN, 끝에 `.` 필수). 예: `www.example.com.`
    - **type**: 레코드 타입 (`A`, `AAAA`, `CNAME`, `MX`, `TXT`, `NS`, `SRV`, `PTR` 등)
    - **ttl**: TTL (초 단위, 기본값 3600)
    - **records**: 레코드 값 목록
      - `content`: 레코드 값 (예: A → `192.168.1.1`, MX → `10 mail.example.com.`)
      - `disabled`: 비활성화 여부 (기본값 false)

    같은 이름/타입의 레코드가 이미 존재하면 덮어씁니다.
    """
    rrset = {
        "name": record.name,
        "type": record.type.upper(),
        "ttl": record.ttl,
        "changetype": "REPLACE",
        "records": [r.model_dump() for r in record.records],
    }
    await pdns_client.update_records(zone_id, [rrset])
    return RecordResponse(message="Record created", name=record.name, type=record.type)


@router.put(
    "",
    summary="레코드 수정",
    response_model=RecordResponse,
    response_description="수정 결과",
    responses={
        404: {"description": "Zone을 찾을 수 없음"},
    },
)
async def update_record(
    record: RecordUpdate,
    zone_id: str = Path(..., description="Zone ID", example="example.com."),
):
    """
    기존 DNS 레코드를 수정합니다.

    해당 이름/타입의 레코드를 새로운 값으로 교체합니다 (REPLACE 방식).
    TTL과 레코드 값을 변경할 수 있습니다.
    """
    rrset = {
        "name": record.name,
        "type": record.type.upper(),
        "ttl": record.ttl,
        "changetype": "REPLACE",
        "records": [r.model_dump() for r in record.records],
    }
    await pdns_client.update_records(zone_id, [rrset])
    return RecordResponse(message="Record updated", name=record.name, type=record.type)


@router.post(
    "/batch",
    summary="레코드 일괄 생성/수정",
    response_model=BatchRecordResponse,
    response_description="일괄 처리 결과",
)
async def batch_update_records(
    records: list[RecordCreate],
    zone_id: str = Path(..., description="Zone ID", example="example.com."),
):
    """
    여러 DNS 레코드를 한번에 생성/수정합니다.

    레코드 목록을 배열로 전달하면 하나의 트랜잭션으로 처리됩니다.
    각 레코드에 대해 같은 이름/타입이 이미 존재하면 덮어씁니다.
    """
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
    return BatchRecordResponse(message=f"{len(records)} records updated")


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="레코드 삭제",
    response_description="삭제 완료",
    responses={
        404: {"description": "Zone을 찾을 수 없음"},
    },
)
async def delete_record(
    record: RecordDelete,
    zone_id: str = Path(..., description="Zone ID", example="example.com."),
):
    """
    DNS 레코드를 삭제합니다.

    지정한 이름과 타입에 해당하는 레코드를 완전히 삭제합니다.

    **주의**: 이 작업은 되돌릴 수 없습니다.
    """
    rrset = {
        "name": record.name,
        "type": record.type.upper(),
        "changetype": "DELETE",
    }
    await pdns_client.update_records(zone_id, [rrset])
