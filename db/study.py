import uuid
from sqlalchemy import select  # , joinedload,selectinload
from db.model import StudyConfiguration
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.study_config_schema import StudyConfig

"""
Example async methods to show how to interact
with the database using SQLAlchemy
"""

#SELECT
async def get_study(id: uuid.UUID, conn: AsyncSession):
    stmt = select(StudyConfiguration).where(StudyConfiguration.id == id)
    result = await conn.execute(stmt)
    study = result.scalars().first()
    return StudyConfig.model_validate(study)

#INSERT
async def add_study(study: StudyConfig, conn: AsyncSession):
    _study = StudyConfiguration(show_results=study.show_results)
    # INSERT
    conn.add(_study)
    # COMMIT CHANGE
    await conn.commit()