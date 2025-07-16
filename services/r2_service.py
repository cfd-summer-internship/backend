from botocore.client import BaseClient
from fastapi import HTTPException, UploadFile
from botocore.exceptions import ClientError


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
    
def upload_zip_to_bucket(
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
