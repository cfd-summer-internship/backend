from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from models.study_response_model import StudyResponse
from schemas.study_results_schema import StudyResponseSchema
from fastapi import HTTPException

async def store_study_responses(
    study_results_id: UUID, responses: list[StudyResponseSchema], conn: AsyncSession
):
    try:
        for i,response in enumerate(responses):
            conn.add(StudyResponse(
                id=i+1,
                study_results_id = study_results_id,
                image_id=response.image_id,
                response_time=response.response_time,
                answer=response.answer
            ))
        await conn.commit()
    except Exception as e:
        await conn.rollback()
        raise HTTPException(404,str(e))