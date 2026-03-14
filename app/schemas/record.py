from pydantic import BaseModel, Field


class RecordItem(BaseModel):
    content: str = Field(..., description="Record content, e.g. '192.168.1.1' for A record")
    disabled: bool = Field(False, description="Whether this record is disabled")


class RecordCreate(BaseModel):
    name: str = Field(..., description="Record name (FQDN), e.g. www.example.com.")
    type: str = Field(..., description="Record type: A, AAAA, CNAME, MX, TXT, NS, SRV, PTR, etc.")
    ttl: int = Field(3600, description="TTL in seconds")
    records: list[RecordItem] = Field(..., description="Record values")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "www.example.com.",
                    "type": "A",
                    "ttl": 3600,
                    "records": [{"content": "192.168.1.1", "disabled": False}],
                }
            ]
        }
    }


class RecordUpdate(BaseModel):
    name: str = Field(..., description="Record name (FQDN)")
    type: str = Field(..., description="Record type")
    ttl: int = Field(3600, description="TTL in seconds")
    records: list[RecordItem] = Field(..., description="Updated record values")


class RecordDelete(BaseModel):
    name: str = Field(..., description="Record name (FQDN)")
    type: str = Field(..., description="Record type")
