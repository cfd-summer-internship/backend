import uuid
from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from db.client import get_db_session
from db.study import add_study, get_study
from sqlalchemy.ext.asyncio import AsyncSession


class StudyConfig(BaseModel):
    show_results: bool
    model_config = ConfigDict(from_attributes=True)


# ROUTER
router = APIRouter(prefix="/config", tags=["Config"])


@router.post("/add", response_model=None)
async def add_configuration(
    study: StudyConfig, conn: AsyncSession = Depends(get_db_session)
):
    await add_study(study=study, conn=conn)

@router.get("/retrieve", response_model=StudyConfig)
async def get_configuration(
    id:uuid.UUID, conn: AsyncSession = Depends(get_db_session)
):
    study = await get_study(id=id, conn=conn)
    return study
