from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from models.study_response_model import StudyResponse
from schemas.study_response_schema import ExperimentResponse

async def store_experiment_responses(
    study_results_id: UUID,
    responses: list[ExperimentResponse],
    conn: AsyncSession
):
    stmt = insert(StudyResponse).values([
        {
            "study_results_id": study_results_id,
            "image_id": response.image_id,
            "response_time": response.response_time,
            "answer": response.answer
        }
        for response in responses
    ])
    await conn.execute(stmt)
    await conn.commit()