from fastapi import APIRouter, Depends
from fastapi.params import Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from db.client import get_db_session
from schemas.study_results_schema import StudyResponseSchema
from services.study_results_service import add_study_result
from services.study_response_service import store_study_responses
from schemas.study_config_response_schema import MessageResponse

router = APIRouter(prefix="/results", tags=["Study Results"])

@router.post("/responses/{study_id}")
async def submit_study_responses(
    study_id: UUID,
    payload: list[StudyResponseSchema],
    subject_id:UUID = Query(...),
    conn: AsyncSession = Depends(get_db_session)
):
    #CURRENTLY A SUBJECT CAN ONLY PERFORM THE EXPERIMENT ONCE
    #CAN BE CHANGED BY REMOVED UNIQUE CONSTRAINT ON SUBJECT ID
    study_result_id = await add_study_result(study_id,subject_id,conn)
    await store_study_responses(study_result_id, payload, conn)  
    return MessageResponse(message="ok")

