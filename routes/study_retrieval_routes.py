# ROUTER
import uuid
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from db.client import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from models.uploaded_files_model import UploadedFiles
from services.study_retrieval_service import (
    get_study_id_list,
    get_study_id,
    get_file_from_db,
)

router = APIRouter(prefix="/study", tags=["study"])


@router.get("/study_ids")
async def get_all_study_ids(
    conn: AsyncSession = Depends(get_db_session),
) -> list[uuid.UUID]:
    """
    Returns a list of all Study ID's from database
    """
    return await get_study_id_list(conn=conn)


@router.get("/study_id/{study_code}")
async def get_study_id_from_code(
    study_code: str,
    conn: AsyncSession = Depends(get_db_session),
) -> uuid.UUID:
    """Return the full study UUID from a submitted 6-digit code."""
    return await get_study_id(study_code, conn=conn)


@router.get("/consent_form/{study_id}")
async def get_study_consent_form(
    study_id: uuid.UUID,
    conn: AsyncSession = Depends(get_db_session),
) -> StreamingResponse:
    """Returns Consent form as a streaming response of bytes."""
    return await get_file_from_db(
        study_id, 
        UploadedFiles.consent_form, 
        UploadedFiles.consent_form_bytes, 
        conn
    )


@router.get("/instructions/{study_id}")
async def get_study_instructions(
    study_id: uuid.UUID,
    conn: AsyncSession = Depends(get_db_session),
) -> StreamingResponse:
    """Returns Study Instructions as a streaming response of bytes."""
    return await get_file_from_db(
        study_id,
        UploadedFiles.study_instructions,
        UploadedFiles.study_instructions_bytes,
        conn,
    )


@router.get("/debrief/{study_id}")
async def get_study_debrief(
    study_id: uuid.UUID,
    conn: AsyncSession = Depends(get_db_session),
) -> StreamingResponse:
    """Fetches Study Debrief as a streaming response of bytes."""
    return await get_file_from_db(
        study_id, 
        UploadedFiles.study_debrief, 
        UploadedFiles.study_debrief_bytes, 
        conn
    )
