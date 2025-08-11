from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class FileInfo(BaseModel):
    filename:str
    last_modified:datetime
    size:int

class FileInfoList(BaseModel):
    files:list[FileInfo]

class PaginateResponse(BaseModel):
    files: list[FileInfo]
    next_token:Optional[str] = None
    