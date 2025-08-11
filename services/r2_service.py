import mimetypes
from botocore.client import BaseClient
from fastapi import HTTPException, UploadFile
from botocore.exceptions import ClientError
import zipfile
import pathlib


def generate_image_url(client: BaseClient, bucket: str, object_name: str,expiration=3600):
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
            'get_object',
            Params={'Bucket':bucket, 'Key':object_name},
            ExpiresIn=expiration
        )
        return response
    except ClientError as e:
        print("Error Fetching: ", str(e))
        raise HTTPException(404, detail=str(e))
    
def upload_file_to_bucket(
    client:BaseClient, 
    bucket:str, 
    object_name:str,
    file: UploadFile):
    try:
        key = f'{object_name}' #Might insert a custom path here if needed
        client.upload_fileobj(file.file,bucket,key)
        return {"status":"ok"}
    except Exception as e:
        print("Error Uploading: ", str(e))
        raise HTTPException(500, detail=str(e))

def generate_url_list(client:BaseClient, bucket:str, image_list:list[str], expiration=3600) -> list[str]:
    try:
        generated_urls = []
        for image_key in image_list:
            response = client.generate_presigned_url(
                'get_object',
                Params={'Bucket':bucket, 'Key':image_key},
                ExpiresIn=expiration
            )
            if response:
                generated_urls.append(response)
        return generated_urls
    except ClientError as e:
        print("Error Fetching: ", str(e))
        raise HTTPException(404, detail=str(e))

def upload_zip_file(
    client:BaseClient, 
    bucket:str, 
    zip_file: UploadFile,
    prefix:str):
    #VALIDATE FILE TYPE
    if not zip_file.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Must upload a .zip file")
    try:
        zf = zipfile.ZipFile(zip_file.file)
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid ZIP archive")
    
    #VALIDATE FILE NAME
    zf = zipfile.ZipFile(zip_file.file)
    for item in zf.infolist():
        if item.is_dir():
            continue
        #SANITIZE FILENAME
        raw_path = pathlib.PurePosixPath(item.filename)
        safe_parts=[p for p in raw_path if p not in ("",".","..")]
        if not safe_parts:
            continue

        safe_key=pathlib.PurePosixPath(prefix,safe_parts[-1])

        with zf.open(item) as extracted_file:
            content_type = mimetypes.guess_type(safe_parts[-1])
            extra_args={}
            if content_type:
                extra_args["ContentType"] = content_type

        try:
            client.upload_fileobj(
                Fileobj=extracted_file,
                Bucket=bucket,
                Key=str(safe_key),
                ExtraArgs=extra_args
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed uploading '{item.filename}': {e}"
            )
    return {
        "detail": (
            f"Uploaded files from {zip_file.filename} "
            f"to bucket '{bucket}' under prefix '{prefix}' "
        )
    }

