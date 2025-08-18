from uuid import UUID
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from models.study_config_model import StudyConfiguration as StudyConfigModel
except ImportError:
    from models.study_config_model import StudyConfig as StudyConfigModel  # fallback


async def get_config_ids_for_researcher(
    researcher_id: UUID, db: AsyncSession
) -> List[UUID]:
    q = select(StudyConfigModel.id).where(StudyConfigModel.researcher_id == researcher_id)
    result = await db.execute(q)
    return list(result.scalars().all())
