import uuid
from fastapi import APIRouter, Depends, Form, UploadFile, File
from pydantic import BaseModel, ConfigDict
from db.client import get_db_session
from db.study import add_study, get_study
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.study_config_schema import LearningPhase, FileUploads


class StudyConfig(BaseModel):
    show_results: bool
    model_config = ConfigDict(from_attributes=True)


# ROUTER
router = APIRouter(prefix="/config", tags=["Config"])

"""
Helper Functions to map incoming multipart/form-data
into their corresponding pydantic models.
This will help with database insertion and type enforcement.
"""
def getLearningPhase(
        displayDuration:int = Form(...,alias="learning.displayDuration"), #(...)
        pauseDuration:int = Form(...,alias="learning.pauseDuration"),
        displayMethod:str = Form(...,alias="learning.displayMethod")
):
    return LearningPhase(
        display_duration=displayDuration,
        pause_duration=pauseDuration,
        display_method=displayMethod
    )

def getFileUploads(
        consentForm:UploadFile = File(...,alias="configFiles.consentForm"),
        studyInstructions:UploadFile = File(...,alias="configFiles.studyInstructions")
):
    return FileUploads(
        consent_form=consentForm,
        study_instructions=studyInstructions
    )

"""
Test API to show how to take in the multipart/form-data
Can then be dissemenated into database
"""
@router.post("/save")
async def save_configuration(
    learning:LearningPhase = Depends(getLearningPhase),
    files:FileUploads = Depends(getFileUploads)
    ):
    if learning and files:
        return {"message":"Configuration Succesfully Submitted"}

"""
Example APIs to show how to insert and retrieve data from
the database using the established connection method
"""
@router.post("/add", response_model=None)
async def add_configuration(
    study: StudyConfig, conn: AsyncSession = Depends(get_db_session)
):
    await add_study(study=study, conn=conn)


@router.get("/retrieve", response_model=StudyConfig)
async def get_configuration(
    id: uuid.UUID, conn: AsyncSession = Depends(get_db_session)
):
    study = await get_study(id=id, conn=conn)
    return study
