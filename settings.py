from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    postgres_host:str
    postgres_user:str
    postgres_password:str | None=None
    postgres_database: str
    connection_string:str

    #Load ENV File
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
def get_settings():
    return Settings()