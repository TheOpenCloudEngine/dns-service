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
