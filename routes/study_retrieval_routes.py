# ROUTER
import uuid
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from db.client import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from models.uploaded_files_model import UploadedFiles
from services.r2_client import get_r2_client
from settings import Settings, get_settings
from botocore.client import BaseClient
from schemas.study_config_response_schema import StudyConfigResponse
from services.study_retrieval_service import (
    get_config_file,
    get_study_id_list,
    get_study_id,
    get_file_from_db,
    get_learning_phase_data,
    get_experiment_phase_from_db, get_experiment_phase_data,
)

router = APIRouter(prefix="/study", tags=["Study"])


@router.get("/study_ids")
async def get_all_study_ids(
    conn: AsyncSession = Depends(get_db_session),
) -> list[uuid.UUID]:
    """Returns a list of all Study ID's from database"""
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
        study_id, UploadedFiles.consent_form, UploadedFiles.consent_form_bytes, conn
    )


@router.get("/study_instructions/{study_id}")
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


@router.get("/study_debrief/{study_id}")
async def get_study_debrief(
    study_id: uuid.UUID,
    conn: AsyncSession = Depends(get_db_session),
) -> StreamingResponse:
    """Fetches Study Debrief as a streaming response of bytes."""
    return await get_file_from_db(
        study_id, UploadedFiles.study_debrief, UploadedFiles.study_debrief_bytes, conn
    )


@router.get("/export/{study_id}", response_model=StudyConfigResponse)
async def export_config_file(
    study_id: uuid.UUID,
    conn: AsyncSession = Depends(get_db_session),
) -> StudyConfigResponse:
    """Returns Full Configuration File as a JSON"""
    return await get_config_file(study_id=study_id, conn=conn)


@router.get("/learning_phase/{study_id}")
async def get_learning_phase(
    study_id: uuid.UUID,
    conn: AsyncSession = Depends(get_db_session),
    client: BaseClient = Depends(get_r2_client),
    settings: Settings = Depends(get_settings)
):
    """Returns the Learning Phase configuration for the study."""
    return await get_learning_phase_data(study_id=study_id, conn=conn, client=client, settings=settings)


@router.get("/experiment_phase/{study_id}")
async def get_experiment_phase_images(
    study_id: uuid.UUID,
    conn: AsyncSession = Depends(get_db_session),
    client: BaseClient = Depends(get_r2_client),
    settings: Settings = Depends(get_settings)
):
    """ Returns the Experiment Phase configuration along with presigned URLs for experiment images. """
    return await get_experiment_phase_data(study_id, conn, client, settings)
