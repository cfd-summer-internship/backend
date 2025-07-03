from fastapi import APIRouter, Depends
from db.client import get_db_session
from schemas.study_config_response_schema import MessageResponse
from services.study_config_service import add_study
from services.form_parsers import (
    get_file_uploads,
    get_learning_phase,
    get_wait_phase,
    get_experiment_phase,
    get_conclusion_phase,
)
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.study_config_request_schema import (
    LearningPhaseRequest,
    FileUploadsRequest,
    WaitPhaseRequest,
    ExperimentPhaseRequest,
    ConclusionPhaseRequest,
    StudyConfigRequest,
)


# ROUTER
router = APIRouter(prefix="/config", tags=["Config"])


@router.post("/add", response_model=MessageResponse)
async def add_configuration(
    learning: LearningPhaseRequest = Depends(get_learning_phase),
    waiting: WaitPhaseRequest = Depends(get_wait_phase),
    experiment: ExperimentPhaseRequest = Depends(get_experiment_phase),
    conclusion: ConclusionPhaseRequest = Depends(get_conclusion_phase),
    files: FileUploadsRequest = Depends(get_file_uploads),
    conn: AsyncSession = Depends(get_db_session),
) -> dict:
    """
    Insert a new study configuration

    Takes in a multipart/form-data that consists of value for each corresponding phase  
    """
    study = StudyConfigRequest(
        learning=learning,
        wait=waiting,
        experiment=experiment,
        conclusion=conclusion,
        files=files,
    )

    await add_study(config=study, conn=conn)
    return {"message": "Configuration added succesfully"}
