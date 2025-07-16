from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    #POSTGRES
    postgres_host:str
    postgres_user:str
    postgres_password:str | None=None
    postgres_database: str
    #CONNECTION STRINGS
    connection_string:str
    model_string:str
    #R2
    r2_account_id:str
    r2_access_key_id:str
    r2_secret_access_key:str
    r2_bucket_name:str

    #Load ENV File
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
def get_settings():
    return Settings()