from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from models.survey_answers_model import SurveyAnswer
from schemas.survey_answer_schema import SurveyAnswerResponse


async def save_survey_answer(answer: SurveyAnswerResponse, conn: AsyncSession):
    try:
        db_answer = SurveyAnswer(
            subject_id=answer.subject_id,
            age=answer.age,
            sex=answer.sex,
            race=answer.race
        )
        conn.add(db_answer)
        await conn.commit()
    except SQLAlchemyError as e:
        await conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save answer: {str(e)}")
