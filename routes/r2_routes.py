from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Optional
from uuid import uuid4
from botocore.client import BaseClient
from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile
from fastapi.params import Query
from auth.user_manager import require_role
from models.enums import UserRole
from schemas.r2_schemas import AbortReq, CommitReq, CommitRes, CompleteReq, CompleteRes, CreateReq, CreateRes, DeleteFileRequest, FileInfoList, PaginateResponse, SignPartReq, SignPartRes
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
PRESIGN_TTL = 15 * 60


@router.get("/get_image")
async def get_image_url(
    filename: str,
    settings: Settings = Depends(get_settings),
    client: BaseClient = Depends(get_r2_client),
):
    return generate_image_url(client, settings.r2_bucket_name, filename)


@router.post("/upload")
async def upload_zip(
    prefix: str = "",
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings),
    client: BaseClient = Depends(get_r2_client),
):
    file_type = file.content_type
    if file_type.startswith("image/"):
        return upload_file_to_bucket(client, settings.r2_bucket_name, file.filename, file)
    elif file_type in ("application/zip", "application/x-zip-compressed") or file.filename.lower().endswith(".zip"):
        return upload_zip_file(client, settings.r2_bucket_name, file, prefix)
    else:
        raise HTTPException(415,f"Unsupported Med Type: {file_type}")

@router.delete("/delete_file")
async def delete_file(
    payload: DeleteFileRequest,
    settings: Settings = Depends(get_settings),
    client: BaseClient = Depends(get_r2_client),
):
    return delete_file_from_bucket(client, settings.r2_bucket_name, payload.filename)


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


@router.post("/s3-multipart/create", response_model=CreateRes)
async def create_mpu(
    body: CreateReq,
    user = Depends(require_role(UserRole.STAFF)),
    client: BaseClient = Depends(get_r2_client),
    settings: Settings = Depends(get_settings), # or remove if not multi-tenant
):
    session_id = body.sessionId or "default"
    prefix = user_prefix(user.id, session_id)

    #Add sanitized filename to metadata
    safe_name = safe_filename(body.name)
    metadata = {"owner": str(user.id), "session": session_id, "basename": safe_name}

    key = make_object_key(prefix, safe_name)

    if body.type and body.type.strip():
        resp = client.create_multipart_upload(
            Bucket=settings.r2_bucket_name,
            Key=key,
            ContentType=body.type,
            Metadata=metadata,
        )
    else:
        resp = client.create_multipart_upload(
            Bucket=settings.r2_bucket_name,
            Key=key,
            Metadata=metadata,
        )

    return {"uploadId": resp["UploadId"], "key": key}



def safe_filename(name: str) -> str:
    base = Path(name).name
    return re.sub(r"[^a-zA-Z0-9._-]+", "-", base)[:120] or "file"


def user_prefix(user_id: str, session_id: str) -> str:
    # Choose a shape that matches your needs; keep it consistent everywhere.
    # Examples:
    # - per-user:   staging/u/<user_id>/<session_id>/files/
    # - per-tenant: staging/o/<org_id>/u/<user_id>/<session_id>/files/
    base = f"staging/u/{user_id}"
    return f"{base}/{session_id}/files/"

def make_object_key(prefix: str, original_name: str) -> str:
    return f"{prefix}{uuid4().hex}-{safe_filename(original_name)}"

@router.post("/s3-multipart/sign-part", response_model=SignPartRes)
async def sign_part(
    body: SignPartReq,
    user = Depends(require_role(UserRole.STAFF)),
    client: BaseClient = Depends(get_r2_client),
    settings: Settings = Depends(get_settings),
):
    # Recompute the allowed prefix from claims and derive the sessionId from the key.
    # Minimal pattern: sessionId is the 4th segment after the user/org parts in your scheme.
    # Adjust this parser to your exact key shape.
    # Example parser (quick and dirty):
    try:
        session_id = body.key.split("/")[3]  # [...]/u/<uid>/<session>/files/<uuid>-name
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid key")

    prefix = user_prefix(user.id, session_id)
    try:
        assert_key_under_prefix(body.key, prefix)
    except ValueError:
        raise HTTPException(status_code=403, detail="Key not owned by caller")

    url = client.generate_presigned_url(
        ClientMethod="upload_part",
        Params={
            "Bucket": settings.r2_bucket_name,
            "Key": body.key,
            "UploadId": body.uploadId,
            "PartNumber": body.partNumber,
        },
        ExpiresIn=PRESIGN_TTL,
        HttpMethod="PUT",
    )
    return {"url": url, "headers": {}}


def assert_key_under_prefix(key: str, prefix: str):
    if not key.startswith(prefix):
        raise ValueError("Key outside allowed prefix")
    
@router.post("/s3-multipart/complete", response_model=CompleteRes)
async def complete_mpu(
    body: CompleteReq,
    user = Depends(require_role(UserRole.STAFF)),
    client: BaseClient = Depends(get_r2_client),
    settings: Settings = Depends(get_settings),
):
    # Ownership check
    try:
        session_id = body.key.split("/")[3]
        prefix = user_prefix(user.id, session_id)
        assert_key_under_prefix(body.key, prefix)
    except Exception:
        raise HTTPException(status_code=403, detail="Key not owned by caller")

    parts = [p.normalized() for p in body.parts]
    resp = client.complete_multipart_upload(
        Bucket=settings.r2_bucket_name,
        Key=body.key,
        UploadId=body.uploadId,
        MultipartUpload={"Parts": parts},
    )

    # Optional safety: verify owner metadata still matches the caller
    head = client.head_object(Bucket=settings.r2_bucket_name, Key=body.key)
    if head.get("Metadata", {}).get("owner") != str(user.id):
        # Roll back to be safe
        client.delete_object(Bucket=settings.r2_bucket_name, Key=body.key)
        raise HTTPException(status_code=403, detail="Ownership metadata mismatch")

    # Optional sanity check with expectedSize (from your hook)
    if body.expectedSize is not None and head["ContentLength"] != body.expectedSize:
        client.delete_object(Bucket=settings.r2_bucket_name, Key=body.key)
        raise HTTPException(status_code=409, detail="Size mismatch after complete")
    

    #Overwrite and flatten
    final_key = final_name_from_meta(head, body.key)

    # location = resp.get("Location") or f"s3://{settings.r2_bucket_name}/{body.key}"
    # return {"location": location, "key": body.key, "etag": resp.get("ETag")}
    
    client.copy_object(
        Bucket=settings.r2_bucket_name,
        CopySource={"Bucket": settings.r2_bucket_name, "Key": body.key},
        Key=final_key,                               # <- filename only
        Metadata=head.get("Metadata", {}),           # keep owner/session/basename
        MetadataDirective="REPLACE",
        ContentType=head.get("ContentType", "application/octet-stream"),
    )
    client.delete_object(Bucket=settings.r2_bucket_name, Key=body.key)

    # Return final location + key to the client
    location = f"s3://{settings.r2_bucket_name}/{final_key}"
    return {"location": location, "key": final_key, "etag": resp.get("ETag")}

def final_name_from_meta(head: dict, staging_key: str) -> str:
    meta = head.get("Metadata", {})
    if meta.get("basename"):
        return meta["basename"]
    # Fallback: drop leading "<32hex>-"
    last = staging_key.rsplit("/", 1)[-1]
    return re.sub(r"^[0-9a-f]{32}-", "", last)

@router.delete("/s3-multipart/abort", status_code=204)
async def abort_mpu(
    body: AbortReq,
    user = Depends(require_role(UserRole.STAFF)),
    client: BaseClient = Depends(get_r2_client),
    settings: Settings = Depends(get_settings),
):
    # Same ownership check pattern as above
    try:
        session_id = body.key.split("/")[3]
        prefix = user_prefix(user.id, session_id)
        assert_key_under_prefix(body.key, prefix)
    except Exception:
        raise HTTPException(status_code=403, detail="Key not owned by caller")

    client.abort_multipart_upload(Bucket=settings.r2_bucket_name, Key=body.key, UploadId=body.uploadId)
    return Response(status_code=204)

@router.post("/archives/{sessionId}/commit", response_model=CommitRes)
async def commit_archive(
    sessionId: str,
    body: CommitReq,
    user = Depends(require_role(UserRole.STAFF)),
    client: BaseClient = Depends(get_r2_client),
    settings: Settings = Depends(get_settings),
):
    prefix = user_prefix(user.id, sessionId)

    # Verify every key is under the caller’s prefix and actually owned (via metadata)
    for item in body.items:
        if not item.key.startswith(prefix):
            raise HTTPException(status_code=403, detail=f"Key outside session prefix: {item.key}")
        head = client.head_object(Bucket=settings.r2_bucket_name, Key=item.key)
        if head["ContentLength"] != item.size:
            raise HTTPException(status_code=409, detail=f"Size mismatch for {item.key}")
        if head.get("Metadata", {}).get("owner") != str(user.id):
            raise HTTPException(status_code=403, detail=f"Not owner of {item.key}")

    # Write manifest under the *same* scoped area
    manifest_key = prefix.replace("/files/", "/") + "manifest.json"
    client.put_object(
        Bucket=settings.r2_bucket_name,
        Key=manifest_key,
        Body=json.dumps({
            "userId": str(user.id),
            "sessionId": sessionId,
            "items": [i.model_dump() for i in body.items],
            "version": 1,
            "createdAt": datetime.now(timezone.utc).isoformat(),
        }, separators=(",", ":")).encode(),
        ContentType="application/json",
    )

    # Optional: copy to final/ with same scoping
    # ...

    return {"ok": True, "manifestKey": manifest_key}