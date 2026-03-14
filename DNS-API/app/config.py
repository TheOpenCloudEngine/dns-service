from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    pdns_api_url: str = "http://localhost:15001"
    pdns_api_key: str = "NzR1MnpMVjlqNWhmbWlq"
    pdns_server_id: str = "localhost"
    admin_username: str = "admin"
    admin_password: str = "admin"

    model_config = {"env_prefix": "DNS_SERVICE_"}


settings = Settings()
