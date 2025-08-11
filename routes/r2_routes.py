from botocore.client import BaseClient
from fastapi import APIRouter, Depends, File, UploadFile
from services.r2_client import get_r2_client
from services.r2_service import generate_image_url, upload_file_to_bucket, upload_zip_file
from settings import Settings, get_settings

# ROUTER
router = APIRouter(prefix="/images", tags=["images"])


@router.get("/get_image")
async def get_image_url(
    filename: str,
    settings: Settings = Depends(get_settings),
    client: BaseClient = Depends(get_r2_client),
):
    return generate_image_url(client, settings.r2_bucket_name, filename)


@router.post("/upload_file")
async def upload_file(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings),
    client: BaseClient = Depends(get_r2_client),
):
    return upload_file_to_bucket(client, settings.r2_bucket_name, file.filename, file)

@router.post("/upload_zip")
async def upload_zip(
    zip_file: UploadFile = File(...),
    settings: Settings = Depends(get_settings),
    client: BaseClient = Depends(get_r2_client)
):
    return upload_zip_file(client,settings.r2_bucket_name,zip_file)