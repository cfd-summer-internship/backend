from fastapi import APIRouter, Depends
# from fastapi.params import Query
from sqlalchemy.ext.asyncio import AsyncSession
from db.client import get_db_session
from schemas.study_results_schema import StudyResultsPayload
from services.study_results_service import add_study_result
from services.study_response_service import store_study_responses
from schemas.study_config_response_schema import MessageResponse

router = APIRouter(prefix="/results", tags=["Study Results"])


@router.post("/responses/")
async def submit_study_responses(
    payload: StudyResultsPayload, 
    conn: AsyncSession = Depends(get_db_session)
) -> MessageResponse:
    # NOTE: Each subject can only have one submission per configuration.
    study_result_id = await add_study_result(
        study_id=payload.identity.study_id,
        config_id=payload.identity.config_id,
        subject_id=payload.identity.subject_id,
        conn=conn,
    )

    success = await store_study_responses(
        study_results_id=study_result_id, 
        responses=payload.responses, 
        conn=conn
    )

    if success:
        return MessageResponse(message="Results Submitted Successfully")
