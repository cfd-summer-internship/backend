from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # POSTGRES
    postgres_host: str
    postgres_user: str
    postgres_password: str | None = None
    postgres_database: str
    # CONNECTION STRINGS
    connection_string: str
    model_string: str
    # R2
    r2_account_id: Optional[str] = None
    r2_bucket_name: Optional[str] = None
    #READ-ONLY
    r2_read_access_key_id: Optional[str] = None
    r2_read_secret_access_key: Optional[str] = None
    #READ-WRITE
    r2_rw_access_key_id: Optional[str] = None
    r2_rw_secret_access_key: Optional[str] = None
    #AUTH
    auth:Optional[str] = None
    dev_email:Optional[str] = None
    dev_password:Optional[str] = None

    # Load ENV File
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings():
    return Settings()
