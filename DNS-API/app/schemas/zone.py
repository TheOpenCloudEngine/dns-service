from pydantic import BaseModel, Field


class NameserverInfo(BaseModel):
    nameserver: str = Field(..., description="NS record value, e.g. ns1.example.com.")
    ip: str | None = Field(None, description="Glue record IP (optional)")


class ZoneCreate(BaseModel):
    name: str = Field(..., description="Zone name (FQDN with trailing dot), e.g. example.com.")
    kind: str = Field("Native", description="Zone kind: Native, Master, Slave")
    nameservers: list[str] = Field(
        default_factory=list,
        description="List of nameservers, e.g. ['ns1.example.com.', 'ns2.example.com.']",
    )
    masters: list[str] = Field(
        default_factory=list,
        description="Master IPs for Slave zones",
    )
    soa_edit_api: str = Field("DEFAULT", description="SOA-EDIT-API setting")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "example.com.",
                    "kind": "Native",
                    "nameservers": ["ns1.example.com.", "ns2.example.com."],
                }
            ]
        }
    }


class ZoneUpdate(BaseModel):
    kind: str | None = Field(None, description="Zone kind: Native, Master, Slave")
    masters: list[str] | None = Field(None, description="Master IPs for Slave zones")
    account: str | None = Field(None, description="Zone account")
    soa_edit: str | None = None
    soa_edit_api: str | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "kind": "Master",
                    "soa_edit_api": "EPOCH",
                }
            ]
        }
    }


class ZoneSummary(BaseModel):
    """Zone 목록 조회 시 반환되는 요약 정보"""
    id: str = Field(..., description="Zone ID (FQDN)")
    name: str = Field(..., description="Zone name")
    kind: str = Field(..., description="Zone kind (Native, Master, Slave)")
    serial: int = Field(..., description="SOA serial number")
    notified_serial: int = Field(0, description="Last notified serial")
    account: str = Field("", description="Zone account")
    dnssec: bool = Field(False, description="DNSSEC enabled")


class RRSetRecord(BaseModel):
    """개별 DNS 레코드 값"""
    content: str = Field(..., description="Record value")
    disabled: bool = Field(False, description="Whether record is disabled")


class RRSet(BaseModel):
    """Resource Record Set"""
    name: str = Field(..., description="Record name (FQDN)")
    type: str = Field(..., description="Record type (A, AAAA, CNAME, etc.)")
    ttl: int = Field(..., description="TTL in seconds")
    records: list[RRSetRecord] = Field(default_factory=list, description="Record values")
    comments: list[dict] = Field(default_factory=list, description="Comments")


class ZoneDetail(BaseModel):
    """Zone 상세 조회 시 반환되는 정보"""
    id: str = Field(..., description="Zone ID")
    name: str = Field(..., description="Zone name")
    kind: str = Field(..., description="Zone kind")
    serial: int = Field(..., description="SOA serial")
    notified_serial: int = Field(0)
    account: str = Field("")
    dnssec: bool = Field(False)
    rrsets: list[RRSet] = Field(default_factory=list, description="DNS 레코드 목록")
