from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from db.client import get_db_session
from schemas.study_response_schema import ExperimentResponseList
from services.study_response_service import store_experiment_responses

router = APIRouter(prefix="/experiment", tags=["Experiment Phase"])

@router.post("/responses/{study_results_id}")
async def submit_experiment_responses(
    study_results_id: UUID,
    payload: ExperimentResponseList,
    conn: AsyncSession = Depends(get_db_session)
):
    await store_experiment_responses(study_results_id, payload.responses, conn)
    return {"status": "success"}
