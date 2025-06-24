import uuid
from sqlalchemy import select  # , joinedload,selectinload
from models import study_config_model as StudyConfiguration
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.study_config_schema import StudyConfig, LearningPhase, FileUploads
from fastapi import  Form, UploadFile, File


"""
Helper Functions to map incoming multipart/form-data
into their corresponding pydantic models.
This will help with database insertion and type enforcement.

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
