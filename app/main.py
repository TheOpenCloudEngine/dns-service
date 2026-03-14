import secrets

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.config import settings
from app.routers import records, zones
from app.services.pdns_client import pdns_client

app = FastAPI(
    title="DNS Service API",
    description="PowerDNS 관리 API - Zone 및 DNS 레코드 관리",
    version="1.0.0",
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


@app.get("/", tags=["Health"])
async def root():
    return {"service": "DNS Service API", "version": "1.0.0", "status": "running"}


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}


@app.get("/api/v1/server", tags=["Server"], dependencies=[Depends(verify_credentials)])
async def server_info():
    """PowerDNS 서버 정보를 반환합니다."""
    return await pdns_client.get_server_info()


@app.get("/api/v1/search", tags=["Search"], dependencies=[Depends(verify_credentials)])
async def search(q: str, max: int = 100, object_type: str = "all"):
    """DNS 레코드, Zone 등을 검색합니다."""
    return await pdns_client.search(q, max, object_type)
