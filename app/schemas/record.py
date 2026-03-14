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

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "www.example.com.",
                    "type": "A",
                    "ttl": 7200,
                    "records": [
                        {"content": "192.168.1.1", "disabled": False},
                        {"content": "192.168.1.2", "disabled": False},
                    ],
                }
            ]
        }
    }


class RecordDelete(BaseModel):
    name: str = Field(..., description="Record name (FQDN)")
    type: str = Field(..., description="Record type")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "www.example.com.",
                    "type": "A",
                }
            ]
        }
    }


class RecordResponse(BaseModel):
    """레코드 생성/수정 응답"""
    message: str = Field(..., description="Result message")
    name: str = Field(..., description="Record name")
    type: str = Field(..., description="Record type")


class BatchRecordResponse(BaseModel):
    """레코드 일괄 처리 응답"""
    message: str = Field(..., description="Result message")
