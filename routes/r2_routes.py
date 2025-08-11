from typing import Optional
from botocore.client import BaseClient
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.params import Query
from schemas.r2_schemas import FileInfoList, PaginateResponse
from services.r2_client import get_r2_client
from services.r2_service import (
    delete_file_from_bucket,
    generate_image_url,
    get_all_files_from_bucket,
    get_file_info_page,
    upload_file_to_bucket,
    upload_zip_file,
)
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
    prefix: str = "",
    zip_file: UploadFile = File(...),
    settings: Settings = Depends(get_settings),
    client: BaseClient = Depends(get_r2_client),
):
    return upload_zip_file(client, settings.r2_bucket_name, zip_file, prefix)


@router.delete("/delete_file")
async def delete_file(
    filename: str,
    settings: Settings = Depends(get_settings),
    client: BaseClient = Depends(get_r2_client),
):
    return delete_file_from_bucket(client, settings.r2_bucket_name, filename)


@router.get("/get_all_file_info", response_model=FileInfoList)
async def get_all_file_info(
    settings: Settings = Depends(get_settings),
    client: BaseClient = Depends(get_r2_client),
) -> FileInfoList:
    return get_all_files_from_bucket(client, settings.r2_bucket_name)


@router.get("/get_file_page", response_model=PaginateResponse)
async def get_file_page(
    max_keys: Optional[int] = Query(1000, ge=1, le=1000),
    next_token: Optional[str] = Query(None, alias="continuation_token"),
    settings: Settings = Depends(get_settings),
    client: BaseClient = Depends(get_r2_client),
) -> PaginateResponse:
    return get_file_info_page(
        client=client,
        bucket=settings.r2_bucket_name,
        next_token=next_token,
        max_keys=max_keys,
    )
