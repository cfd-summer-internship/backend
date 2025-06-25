import uuid
from fastapi import APIRouter, Depends, HTTPException
from db.client import get_db_session
from services.study_config_service import add_study, get_study, getLearningPhase, getFileUploads, parse_study_form, \
    getWaitPhase, getConclusionPhase, getExperimentPhase
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.study_config_schema import LearningPhase, FileUploads, StudyConfig, WaitPhase, ExperimentPhase, \
    ConclusionPhase

# ROUTER
router = APIRouter(prefix="/config", tags=["Config"])

"""
Test API to show how to take in the multipart/form-data
Can then be dissemenated into database
"""


@router.post("/save")
async def save_configuration(
        learning: LearningPhase = Depends(getLearningPhase),
        files: FileUploads = Depends(getFileUploads)
):
    if learning and files:
        return {"message": "Configuration Successfully Submitted"}


"""
Example APIs to show how to insert and retrieve data from
the database using the established connection method
"""


from schemas.study_config_schema import StudyConfig

@router.post("/add")
async def add_configuration(
    learning: LearningPhase = Depends(getLearningPhase),
    waiting: WaitPhase = Depends(getWaitPhase),
    experiment: ExperimentPhase = Depends(getExperimentPhase),
    conclusion: ConclusionPhase = Depends(getConclusionPhase),
    files: FileUploads = Depends(getFileUploads),
    conn: AsyncSession = Depends(get_db_session),
):
    study = StudyConfig(
        learning_phase=learning,
        wait_phase=waiting,
        experiment_phase=experiment,
        conclusion_phase=conclusion,
        file_uploads=files
    )
    await add_study(config=study, conn=conn)
    return {"status": "ok"}




@router.get("/retrieve", response_model=StudyConfig)
async def get_configuration(
        id: uuid.UUID, conn: AsyncSession = Depends(get_db_session)
):
    study = await get_study(id=id, conn=conn)
    if not study:
        raise HTTPException(status_code=404, detail="Study Configuration Not Found!")
    return study
