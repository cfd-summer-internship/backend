from pydantic import BaseModel, ConfigDict
import uuid
from sqlalchemy import select  # , joinedload,selectinload
from db.model import StudyConfiguration
from sqlalchemy.ext.asyncio import AsyncSession


class StudyConfig(BaseModel):
    show_results: bool
    model_config = ConfigDict(from_attributes=True)


# async def get_study(
#         id:uuid.UUID,
#         conn:AsyncSession = Depends(get_db_session())
#         ):
#     sel_query = select(StudyConfiguration).where(StudyConfiguration.id==id).options(
#         joinedload(StudyConfiguration.files),
#         joinedload(StudyConfiguration.learning),
#         joinedload(StudyConfiguration.wait),
#         joinedload(StudyConfiguration.experiment),
#         selectinload(StudyConfiguration.survey).
#             selectinload(DemographicSurvey.questions),
#         selectinload(StudyConfiguration.survey).
#             selectinload(DemographicSurvey.answers)
#     )

#     result = await conn.execute(sel_query)
#     return result.scalars().all()


async def get_study(id: uuid.UUID, conn: AsyncSession):
    stmt = select(StudyConfiguration).where(StudyConfiguration.id == id)
    result = await conn.execute(stmt)
    study = result.scalars().first()
    return StudyConfig.model_validate(study)


async def add_study(study: StudyConfig, conn: AsyncSession):
    _study = StudyConfiguration(show_results=study.show_results)
    # INSERT
    conn.add(_study)
    # COMMIT CHANGE
    await conn.commit()
