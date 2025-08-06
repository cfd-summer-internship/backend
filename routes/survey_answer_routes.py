from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from db.client import get_db_session
from models.survey_answers_model import SurveyAnswer
from schemas.survey_answer_schema import SurveyAnswerCreate

router = APIRouter(prefix="/survey-answer", tags=["Survey Answer"])

@router.post("/", status_code=status.HTTP_201_CREATED)
async def store_survey_answer(
    answer: SurveyAnswerCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """Store a survey answer linked to a survey config and question. Currently supports one answer per question due to unique constraint"""
    new_answer = SurveyAnswer(
        survey_config_id=answer.survey_config_id,
        survey_question_id=answer.survey_question_id,
        text=answer.text
    )

    db.add(new_answer)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Answer for this question already exist."
        )

    return {"message": "Survey answer stored successfully"}
