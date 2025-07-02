
# ROUTER
import uuid
from fastapi import APIRouter, Depends
from db.client import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from services.study_retrieval_service import get_study_id_list, get_consent_form,get_study_id


router = APIRouter(prefix="/study", tags=["study"])

@router.get("/study_ids")
async def get_all_study_ids(
        conn: AsyncSession = Depends(get_db_session),
) -> list[uuid.UUID]:
    return await get_study_id_list(conn=conn)

@router.get("/study_id/{study_code}")
async def get_study_id_from_code(
        study_code:str,
        conn: AsyncSession = Depends(get_db_session),
) -> uuid.UUID:
    return await get_study_id(study_code,conn=conn)

@router.get("/consent_form/{study_id}")
async def get_study_consent_form(
    study_id: uuid.UUID,
    conn: AsyncSession = Depends(get_db_session),
):
    return await get_consent_form(study_id,conn)
