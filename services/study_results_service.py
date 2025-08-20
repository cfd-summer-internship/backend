from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID, uuid4
from models.study_result_model import StudyResults
from datetime import datetime

from schemas.study_results_schema import StudyResult
from services.study_retrieval_service import get_study_id_from_config


async def add_study_result(config_id: UUID, subject_id: UUID, conn: AsyncSession):
    '''Creates a corresponding Study Result for each submission.
    Only commited if Study Responses are successfully inserted.'''
    try:
        study_id = await get_study_id_from_config(config_id=config_id, conn=conn)
        study_result = StudyResults(
            id=uuid4(),
            study_id=study_id,
            config_id=config_id,
            subject_id=subject_id,
            submitted=datetime.now(),
        )
        conn.add(study_result)
        return study_result.id
    except Exception as e:
        print("Error", str(e))
        await conn.rollback()


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
