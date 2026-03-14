import secrets

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.config import settings
from app.routers import records, zones
from app.services.pdns_client import pdns_client

TAGS_METADATA = [
    {
        "name": "Health",
        "description": "서비스 상태 확인",
    },
    {
        "name": "Zones",
        "description": "DNS Zone 관리 - 생성, 조회, 수정, 삭제 및 Zone 전송 관련 기능",
    },
    {
        "name": "Records",
        "description": "DNS 레코드(호스트) 관리 - A, AAAA, CNAME, MX, TXT, NS, SRV 등 레코드 CRUD",
    },
    {
        "name": "Server",
        "description": "PowerDNS 서버 정보 조회",
    },
    {
        "name": "Search",
        "description": "DNS 레코드 및 Zone 검색",
    },
]

app = FastAPI(
    title="DNS Service API",
    description="""
## PowerDNS 관리 API

PowerDNS Authoritative Server를 위한 RESTful 관리 API입니다.

### 주요 기능

- **Zone 관리**: DNS Zone 생성, 조회, 수정, 삭제
- **레코드 관리**: A, AAAA, CNAME, MX, TXT, NS, SRV 등 DNS 레코드 CRUD
- **일괄 처리**: 여러 레코드를 한번에 생성/수정
- **검색**: Zone 및 레코드 검색

### 인증

모든 API 엔드포인트는 **HTTP Basic Authentication**을 사용합니다.

### 참고

- Zone 이름과 레코드 이름은 반드시 FQDN 형식이어야 합니다 (끝에 `.` 포함).
- 예: `example.com.`, `www.example.com.`
""",
    version="1.0.0",
    openapi_tags=TAGS_METADATA,
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "DNS Service Admin",
    },
    license_info={
        "name": "MIT",
    },
)

security = HTTPBasic()


def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, settings.admin_username)
    correct_password = secrets.compare_digest(credentials.password, settings.admin_password)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


app.include_router(zones.router, prefix="/api/v1", dependencies=[Depends(verify_credentials)])
app.include_router(records.router, prefix="/api/v1", dependencies=[Depends(verify_credentials)])


@app.get("/", tags=["Health"], summary="서비스 상태")
async def root():
    """서비스 기본 정보와 상태를 반환합니다."""
    return {"service": "DNS Service API", "version": "1.0.0", "status": "running"}


@app.get("/health", tags=["Health"], summary="헬스 체크")
async def health():
    """서비스의 health 상태를 반환합니다."""
    return {"status": "healthy"}


@app.get(
    "/api/v1/server",
    tags=["Server"],
    summary="PowerDNS 서버 정보",
    dependencies=[Depends(verify_credentials)],
)
async def server_info():
    """
    PowerDNS 서버의 상세 정보를 반환합니다.

    서버 버전, 구성 정보 등을 포함합니다.
    """
    return await pdns_client.get_server_info()


@app.get(
    "/api/v1/search",
    tags=["Search"],
    summary="DNS 검색",
    dependencies=[Depends(verify_credentials)],
)
async def search(
    q: str = Query(..., description="검색어 (Zone 이름, 레코드 이름 또는 값)", example="example"),
    max: int = Query(100, description="최대 결과 수", ge=1, le=1000),
    object_type: str = Query(
        "all",
        description="검색 대상 유형",
        enum=["all", "zone", "record", "comment"],
    ),
):
    """
    DNS 레코드, Zone 등을 검색합니다.

    - **q**: 검색어 (와일드카드 `*` 사용 가능)
    - **max**: 최대 반환 결과 수 (기본값 100)
    - **object_type**: 검색 대상 (`all`, `zone`, `record`, `comment`)
    """
    return await pdns_client.search(q, max, object_type)
