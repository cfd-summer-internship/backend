import uuid
from fastapi import APIRouter, Depends
from db.client import get_db_session
from schemas.study_config_response_schema import StudyConfigResponse
from services.study_config_service import add_study, get_study
from services.form_parsers import get_file_uploads, get_learning_phase, get_wait_phase, get_experiment_phase, get_conclusion_phase
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.study_config_request_schema import LearningPhaseRequest, FileUploadsRequest, WaitPhaseRequest, \
    ExperimentPhaseRequest, \
    ConclusionPhaseRequest, StudyConfigRequest


# ROUTER
router = APIRouter(prefix="/config", tags=["Config"])

"""
Test API to show how to take in the multipart/form-data
Can then be dissemenated into database
"""


@router.post("/save")
async def save_configuration(
        learning: LearningPhaseRequest = Depends(get_learning_phase),
        files: FileUploadsRequest = Depends(get_file_uploads)
):
    if learning and files:
        return {"message": "Configuration Successfully Submitted"}


"""
APIs to insert and retrieve data from
the database using the established connection method
"""



@router.post("/add")
async def add_configuration(
        learning: LearningPhaseRequest = Depends(get_learning_phase),
        waiting: WaitPhaseRequest = Depends(get_wait_phase),
        experiment: ExperimentPhaseRequest = Depends(get_experiment_phase),
        conclusion: ConclusionPhaseRequest = Depends(get_conclusion_phase),
        files: FileUploadsRequest = Depends(get_file_uploads),
        conn: AsyncSession = Depends(get_db_session),
):
    study = StudyConfigRequest(
        learning=learning,
        wait=waiting,
        experiment=experiment,
        conclusion=conclusion,
        files=files
    )

    await add_study(config=study, conn=conn)
    return {"status": "ok"}


@router.get("/retrieve/{study_id}", response_model=StudyConfigResponse)
async def get_configuration(
        study_id: uuid.UUID,
        conn: AsyncSession = Depends(get_db_session),
):
    return await get_study(study_id=study_id, conn=conn)
