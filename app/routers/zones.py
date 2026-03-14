from fastapi import APIRouter, Path, status

from app.schemas.zone import ZoneCreate, ZoneDetail, ZoneSummary, ZoneUpdate
from app.services.pdns_client import pdns_client

router = APIRouter(prefix="/zones", tags=["Zones"])


@router.get(
    "",
    summary="Zone 목록 조회",
    response_model=list[ZoneSummary],
    response_description="Zone 목록",
)
async def list_zones():
    """
    등록된 모든 DNS Zone 목록을 반환합니다.

    각 Zone의 이름, 종류(Native/Master/Slave), SOA 시리얼 등 요약 정보를 포함합니다.
    """
    return await pdns_client.list_zones()


@router.get(
    "/{zone_id}",
    summary="Zone 상세 조회",
    response_model=ZoneDetail,
    response_description="Zone 상세 정보 (레코드 포함)",
)
async def get_zone(
    zone_id: str = Path(..., description="Zone ID (예: example.com.)", example="example.com."),
):
    """
    특정 Zone의 상세 정보를 반환합니다.

    Zone에 속한 모든 DNS 레코드(rrsets)를 포함합니다.
    """
    return await pdns_client.get_zone(zone_id)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Zone 생성",
    response_model=ZoneDetail,
    response_description="생성된 Zone 정보",
    responses={
        409: {"description": "이미 존재하는 Zone"},
        422: {"description": "유효하지 않은 요청 데이터"},
    },
)
async def create_zone(zone: ZoneCreate):
    """
    새 DNS Zone을 생성합니다.

    - **name**: Zone 이름 (FQDN, 끝에 `.` 필수). 예: `example.com.`
    - **kind**: Zone 종류 - `Native`(기본), `Master`, `Slave`
    - **nameservers**: NS 레코드 목록. 예: `["ns1.example.com.", "ns2.example.com."]`
    - **masters**: Slave Zone인 경우 Master 서버 IP 목록
    - **soa_edit_api**: SOA 시리얼 자동 업데이트 방식 (`DEFAULT`, `EPOCH` 등)
    """
    payload = {
        "name": zone.name,
        "kind": zone.kind,
        "nameservers": zone.nameservers,
        "soa_edit_api": zone.soa_edit_api,
    }
    if zone.masters:
        payload["masters"] = zone.masters
    return await pdns_client.create_zone(payload)


@router.put(
    "/{zone_id}",
    summary="Zone 수정",
    response_description="수정 완료 (빈 응답)",
    responses={
        404: {"description": "Zone을 찾을 수 없음"},
    },
)
async def update_zone(
    zone: ZoneUpdate,
    zone_id: str = Path(..., description="Zone ID (예: example.com.)", example="example.com."),
):
    """
    Zone의 설정을 수정합니다.

    변경하려는 필드만 전달하면 됩니다 (부분 업데이트).
    """
    payload = zone.model_dump(exclude_none=True)
    return await pdns_client.update_zone(zone_id, payload)


@router.delete(
    "/{zone_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Zone 삭제",
    response_description="삭제 완료",
    responses={
        404: {"description": "Zone을 찾을 수 없음"},
    },
)
async def delete_zone(
    zone_id: str = Path(..., description="Zone ID (예: example.com.)", example="example.com."),
):
    """
    Zone과 그에 속한 모든 DNS 레코드를 삭제합니다.

    **주의**: 이 작업은 되돌릴 수 없습니다.
    """
    await pdns_client.delete_zone(zone_id)


@router.put(
    "/{zone_id}/axfr-retrieve",
    summary="Slave Zone AXFR 갱신",
    responses={
        404: {"description": "Zone을 찾을 수 없음"},
    },
)
async def axfr_retrieve(
    zone_id: str = Path(..., description="Zone ID", example="example.com."),
):
    """
    Slave Zone의 AXFR 전송을 트리거합니다.

    Master 서버로부터 Zone 데이터를 다시 가져옵니다.
    """
    return await pdns_client.update_zone(zone_id, {})


@router.put(
    "/{zone_id}/notify",
    summary="Zone Notify 전송",
    responses={
        404: {"description": "Zone을 찾을 수 없음"},
    },
)
async def notify_zone(
    zone_id: str = Path(..., description="Zone ID", example="example.com."),
):
    """
    Zone의 Slave 서버들에게 NOTIFY를 전송합니다.

    Master Zone에서 변경이 발생했을 때 Slave에 알리는 용도입니다.
    """
    return await pdns_client.update_zone(zone_id, {})


@router.get(
    "/{zone_id}/export",
    summary="Zone Export (AXFR 형식)",
    response_model=ZoneDetail,
    response_description="Zone 전체 데이터",
)
async def export_zone(
    zone_id: str = Path(..., description="Zone ID", example="example.com."),
):
    """
    Zone 데이터를 전체 내보냅니다.

    Zone의 모든 레코드를 포함한 전체 데이터를 반환합니다.
    """
    return await pdns_client.get_zone(zone_id)
