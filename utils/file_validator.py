#FOR PROD
import magic
from fastapi import UploadFile, HTTPException

ALLOWED_MIME_TYPES = {"application/pdf"}

def validate_file_type(src:UploadFile):
    content = src.file.read()
    mime_type = magic.from_buffer(content, mime=True)

    if mime_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="File Type Not Allowed")
    
    src.file.seek(0)
    return src