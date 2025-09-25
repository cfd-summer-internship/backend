from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional

class FileInfo(BaseModel):
    filename:str
    last_modified:datetime
    size:int

class FileInfoList(BaseModel):
    files:list[FileInfo]

class PaginateResponse(BaseModel):
    files: list[FileInfo]
    next_token:Optional[str] = None

class DeleteFileRequest(BaseModel):
    filename: str
    
#S3-MPU

class CreateReq(BaseModel):
    name: str
    type: Optional[str] = None
    size: Optional[int] = None
    sessionId: Optional[str] = None


class CreateRes(BaseModel):
    uploadId: str
    key: str

class SignPartReq(BaseModel):
    uploadId: str
    key: str
    partNumber: int = Field(gt=0)

class SignPartRes(BaseModel):
    url: str
    headers: dict = {}



def ensure_quoted_etag(etag: str) -> str:
    return etag if etag.startswith('"') and etag.endswith('"') else '"' + etag.strip('"') + '"'


class AwsS3Part(BaseModel):
    ETag: Optional[str] = None
    PartNumber: Optional[int] = None
    etag: Optional[str] = None
    partNumber: Optional[int] = None

    def normalized(self):
        return {
            "ETag": ensure_quoted_etag(self.ETag or self.etag),
            "PartNumber": int(self.PartNumber or self.partNumber),
        }

class CompleteReq(BaseModel):
    uploadId: str
    key: str
    parts: List[AwsS3Part]
    expectedSize: Optional[int] = None 

class CompleteRes(BaseModel):
    location: str
    key: str
    etag: Optional[str] = None


class AbortReq(BaseModel):
    uploadId: str
    key: str


class ManifestItem(BaseModel):
    key: str
    size: int
    sha256: Optional[str] = None

class CommitReq(BaseModel):
    items: List[ManifestItem]

class CommitRes(BaseModel):
    ok: bool
    manifestKey: str