from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID, uuid4
from models.study_result_model import StudyResults
from datetime import datetime

from schemas.study_results_schema import StudyResult


async def add_study_result(study_id: UUID, subject_id: UUID, conn: AsyncSession):
    try:
        study_result = StudyResults(
            id=uuid4(),
            study_id=study_id,
            subject_id=subject_id,
            submitted=datetime.now(),
        )
        conn.add(study_result)
        #await conn.commit()
        return study_result.id
    except Exception as e:
        print("Error", str(e))
        await conn.rollback()
        return None


async def get_study_results(study_id: UUID, conn: AsyncSession):
    """Retrieves all Study Results for a specific study"""
    stmt = select(StudyResults).where(study_id == study_id)
    result = await conn.execute(stmt)
    study_results = result.scalars().all()
    if study_results:
        results = []
        for study in study_results:
            result.append(
                StudyResult(
                    id=study.id,
                    study_id=study.study_id,
                    subject_id=study.subject_id,
                    submitted=study.submitted,
                )
            )
    if results:
        return results

    return None


async def check_for_study_results(study_id: UUID, subject_id:UUID, conn: AsyncSession):
    stmt = select(StudyResults).where(StudyResults.study_id == study_id).where(StudyResults.subject_id==subject_id)
    result = await conn.execute(stmt)
    study_results = result.scalar_one_or_none()
    return study_results
