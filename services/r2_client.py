import boto3
from botocore.client import Config, BaseClient
from settings import get_settings
from functools import lru_cache

settings = get_settings()

@lru_cache()
def get_r2_client() -> BaseClient:
    return boto3.client(
    "s3",
    endpoint_url=f"https://{settings.r2_account_id}.r2.cloudflarestorage.com",
    aws_access_key_id=settings.r2_access_key_id,
    aws_secret_access_key=settings.r2_secret_access_key,
    config=Config(signature_version='s3v4'),
    region_name="auto"
)