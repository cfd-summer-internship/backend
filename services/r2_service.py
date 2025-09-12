import mimetypes
from typing import Optional
from botocore.client import BaseClient
from fastapi import HTTPException, UploadFile
from botocore.exceptions import ClientError
import zipfile
import pathlib

from schemas.r2_schemas import FileInfo, FileInfoList, PaginateResponse


def generate_image_url(
    client: BaseClient, bucket: str, object_name: str, expiration=3600
):
    """Retrieve a presigned url for an image from the specified R2 Bucket

    Args:
        client:
            S3 Client, used for connection to r2 via the S3 API
        bucket:
            Name of the R2 Bucket
        key:
            Name of the file in the bucket
        expiration:
            Time in seconds for the URL to remain valid, defaults to 3600
    Returns:
        Generated presigned image url
    Raises:
        404: Image not found error
    """
    try:
        response = client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": object_name},
            ExpiresIn=expiration,
        )
        return response
    except ClientError as e:
        print("Error Fetching: ", str(e))
        raise HTTPException(404, detail=str(e))


def upload_file_to_bucket(
    client: BaseClient, bucket: str, object_name: str, file: UploadFile
):
    try:
        key = f"{object_name}"  # Might insert a custom path here if needed
        client.upload_fileobj(file.file, bucket, key)
        return {"status": "ok"}
    except Exception as e:
        print("Error Uploading: ", str(e))
        raise HTTPException(500, detail=str(e))


def generate_url_list(
    client: BaseClient, bucket: str, image_list: list[str], expiration=3600
) -> list[str]:
    try:
        generated_urls = []
        for image_key in image_list:
            response = client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket, "Key": image_key},
                ExpiresIn=expiration,
            )
            if response:
                generated_urls.append(response)
        return generated_urls
    except ClientError as e:
        print("Error Fetching: ", str(e))
        raise HTTPException(404, detail=str(e))


def upload_zip_file(client: BaseClient, bucket: str, zip_file: UploadFile, prefix: str):
    """Upload a Zip File to r2

    Args:
        client:
            S3 Client, used for connection to r2 via the S3 API
        bucket:
            Name of the R2 Bucket
        zip_file:
            A fastAPI UploadFile with a .zip extension
        prefix:
            Indicate if you want to upload to a subfolder or specific directory
    Returns:
        200: details: Uploaded File Name, Bucket Name, and Prefix
    Raises:
        500: Upload Failed. Performs a rollback on failure, automatically deletes files that were uploaded to prevent partial uploading of folder.
    """
    # VALIDATE FILE TYPE
    if not zip_file.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Must upload a .zip file")
    try:
        zf = zipfile.ZipFile(zip_file.file)
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid ZIP archive")

    # VALIDATE FILE NAME
    uploaded = []
    zf = zipfile.ZipFile(zip_file.file)
    try:
        for item in zf.infolist():
            if (
                item.is_dir()
                or "DS_Store" in item.filename
                or "__MACOSX" in item.filename
            ):
                continue
            # SANITIZE FILENAME
            raw_path = pathlib.PurePosixPath(item.filename)
            safe_parts = [p for p in raw_path.parts if p not in ("", ".", "..")]
            if not safe_parts:
                continue

            safe_key = pathlib.PurePosixPath(prefix, safe_parts[-1])

            # OPEN FILE AND GET TYPE
            with zf.open(item) as extracted_file:
                content_type, _ = mimetypes.guess_type(safe_parts[-1])
                # ONLY UPLOAD IMAGES
                if content_type != "image/jpeg":
                    continue
                extra_args = {}
                if content_type:
                    extra_args["ContentType"] = content_type
                    # UPLOAD FILE
                    client.upload_fileobj(
                        Fileobj=extracted_file,
                        Bucket=bucket,
                        Key=str(safe_key),
                        ExtraArgs=extra_args,
                    )
                    uploaded.append(safe_key)
    except Exception as e:
        if uploaded:
            client.delete_objects(
                Bucket=bucket,
                Delete={"Objects": [{"Key": k} for k in uploaded]},
            )
        raise HTTPException(
            status_code=500,
            detail=f"Failed uploading, rolled back: '{item.filename}': {e}",
        )
    return {
        "detail": (
            f"Uploaded files from {zip_file.filename} "
            f"to bucket '{bucket}' under prefix '{prefix}' "
        )
    }


def delete_file_from_bucket(client: BaseClient, bucket: str, key: str):
    try:
        client.delete_object(Bucket=bucket, Key=key)
        return {"status": "success"}
    except Exception as e:
        print("Error Uploading: ", str(e))
        raise HTTPException(500, detail=str(e))


def get_all_files_from_bucket(client: BaseClient, bucket: str):
    paginator = client.get_paginator("list_objects_v2")
    all_keys = []
    for page in paginator.paginate(Bucket=bucket):
        for item in page.get("Contents", []):
            all_keys.append(
                FileInfo(
                    filename=item["Key"],
                    last_modified=item["LastModified"],
                    size=item["Size"],
                )
            )

    return FileInfoList(files=all_keys)


def get_file_info_page(
    client: BaseClient, bucket: str, next_token: Optional[str], max_keys: Optional[int]
):
    parameters = {
        "Bucket": bucket,
        "MaxKeys": max_keys,
    }
    if next_token:
        parameters["ContinuationToken"] = next_token

    response = client.list_objects_v2(**parameters)

    if (
        "ResponseMetadata" not in response
        or response["ResponseMetadata"]["HTTPStatusCode"] != 200
    ):
        raise HTTPException(500, "Could not list R2 objects")

    files = [
        FileInfo(
            filename=item["Key"], last_modified=item["LastModified"], size=item["Size"]
        )
        for item in response.get("Contents", [])
    ]
    if response.get("IsTruncated"):
        token = response.get("NextContinuationToken")
        return PaginateResponse(files=files, next_token=token)
    return PaginateResponse(files=files)
