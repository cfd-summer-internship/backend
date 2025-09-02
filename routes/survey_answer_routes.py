from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from db.client import get_db_session
from schemas.survey_answer_schema import SurveyAnswerResponse
from services.survey_answer_service import save_survey_answer

router = APIRouter(prefix="/survey", tags=["Survey"])

@router.post("/responses", status_code=status.HTTP_201_CREATED)
async def submit_survey_answers(
    answer: SurveyAnswerResponse,
    conn: AsyncSession = Depends(get_db_session)
):
    await save_survey_answer(answer, conn)
    return {"message": "Survey answers submitted successfully"}
