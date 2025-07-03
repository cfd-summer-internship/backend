from io import BytesIO
import uuid
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.study_config_model import StudyConfiguration
from models.uploaded_files_model import UploadedFiles


async def get_study_id_list(conn: AsyncSession) -> list[uuid.UUID]:
    """Returns list of all Study ID's from the database or raises an exception error on failure"""
    try:
        stmt = select(StudyConfiguration).execution_options(populate_existing=True)
        result = await conn.execute(stmt)
        ids: list[uuid.UUUID] = []
        rows = result.scalars().all()
        for study in rows:
            ids.append(study.id)
        return ids
    except Exception:
        raise HTTPException(404)


async def get_study_id(study_code: str, conn: AsyncSession) -> uuid.UUID:
    """Returns the first matching Study ID from a submitted 6-digit study code"""
    try:
        stmt = select(StudyConfiguration).execution_options(populate_existing=True)
        result = await conn.execute(stmt)
        rows = result.scalars().all()
        for study in rows:
            if study.id.hex[-6:] == study_code:
                return study.id
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


async def get_file_from_db(
    study_id: uuid.UUID,
    filename: str,
    requested_file: bytes,
    conn: AsyncSession,
    media_type: str = "application/pdf",
) -> StreamingResponse:
    """
    Retrieves raw bytes to be served via a streaming repsonse.

    Args:
        study_id:
            UUID for the requested study
        filename:
            Takes in a string provided by the database model (UploadedFiles.file_name)
        requested_file:
            Takes in the file's bytes provided by the database model (UploadedFiles.file_bytes)
        conn:
            Asyn Connection to the Database
        media_type:
            String value representing mime type. Defaults to "application/pdf"
        
    Returns:
        A Streaming Response of bytes that can be served to the frontend as a BLOB.

        The raw file bytes are casted as a Buffered I/O implementation.
        The media type is dictated by the provided parameter
        Header consists of: {"Content-Disposition": f'inline; filename="{filename}"'},

    Raises:
        HTTPException: 404 File not Found
    """
    try:
        stmt = (
            select(filename, requested_file)
            .where(UploadedFiles.study_config_id == study_id)
            .execution_options(populate_existing=True)
        )
        result = await conn.execute(stmt)
        file = result.first()

        if not file:
            raise HTTPException(status_code=404, detail="File not found")

        return StreamingResponse(
            BytesIO(file[1]),
            media_type=media_type,
            headers={"Content-Disposition": f'inline; filename="{file[0]}"'},
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
