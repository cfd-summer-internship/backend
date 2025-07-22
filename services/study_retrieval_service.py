from io import BytesIO
import uuid

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from models.study_config_model import StudyConfiguration
from models.survey_questions_model import SurveyQuestion
from models.uploaded_files_model import UploadedFiles
from models.user_survey_config_model import UserSurveyConfig
from schemas.study_config_response_schema import StudyConfigResponse
from schemas.study_config_response_schema import (
    FileUploads,
    LearningPhase,
    WaitPhase,
    ExperimentPhase,
    ConclusionPhase, 
    SurveyQuestions
)


async def get_study_id_list(conn: AsyncSession) -> list[uuid.UUID]:
    """Returns list of all Study ID's from the database or raises an exception error on failure"""
    try:
        stmt = select(StudyConfiguration).execution_options(populate_existing=True)
        result = await conn.execute(stmt)
        ids: list[uuid.UUUID] = []
        rows = result.scalars().all()
        for study in rows:
            ids.append(study.id)
        return ids
    except Exception as e:
        raise HTTPException(404, detail=str(e))


async def get_study_id(study_code: str, conn: AsyncSession) -> uuid.UUID:
    """Returns the first matching Study ID from a submitted 6-digit study code"""
    try:
        stmt = select(StudyConfiguration).execution_options(populate_existing=True)
        result = await conn.execute(stmt)
        rows = result.scalars().all()
        for study in rows:
            if study.id.hex[-6:] == study_code:
                return study.id
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


async def get_file_from_db(
    study_id: uuid.UUID,
    filename: str,
    requested_file: bytes,
    conn: AsyncSession,
    media_type: str = "application/pdf",
) -> StreamingResponse:
    """
    Retrieves raw bytes to be served via a streaming repsonse.

    Args:
        study_id:
            UUID for the requested study
        filename:
            Takes in a string provided by the database model (UploadedFiles.file_name)
        requested_file:
            Takes in the file's bytes provided by the database model (UploadedFiles.file_bytes)
        conn:
            Asyn Connection to the Database
        media_type:
            String value representing mime type. Defaults to "application/pdf"

    Returns:
        A Streaming Response of bytes that can be served to the frontend as a BLOB.

        The raw file bytes are casted as a Buffered I/O implementation.
        The media type is dictated by the provided parameter
        Header consists of: {"Content-Disposition": f'inline; filename="{filename}"'},

    Raises:
        HTTPException: 404 File not Found
    """
    try:
        stmt = (
            select(filename, requested_file)
            .where(UploadedFiles.study_config_id == study_id)
            .execution_options(populate_existing=True)
        )
        result = await conn.execute(stmt)
        file = result.first()

        if not file:
            raise HTTPException(status_code=404, detail="File not found")

        return StreamingResponse(
            BytesIO(file[1]),
            media_type=media_type,
            headers={"Content-Disposition": f'inline; filename="{file[0]}"'},
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


async def get_config_file(
    study_id: uuid.UUID, conn: AsyncSession,
    
) -> StudyConfigResponse:
    """
    Returns Configuration File

    Uses a series of join statements to retrieve the entirety of the config file from the database.
    Excludes file bytes but includes filenames for reference.
    Can be used to export the config file for future reference.

    Args:
        study_id:
            UUID for the requested study
        conn:
            Async connection to database

    Returns:
        An instance of StudyConfigResponse serialized as a JSON response.

    Raises:
        HTTPException: 404: Study not found
        HTTPException: 500: Missing file upload data
        HTTPException: 500: Missing phase configuration
    """
    
    stmt = (
        select(StudyConfiguration)
        .options(
            selectinload(StudyConfiguration.learning),
            selectinload(StudyConfiguration.wait),
            selectinload(StudyConfiguration.experiment),
            selectinload(StudyConfiguration.files),
            selectinload(StudyConfiguration.conclusion),
            selectinload(StudyConfiguration.demographics)
            .selectinload(UserSurveyConfig.questions)
        )

        .where(StudyConfiguration.id == study_id)     
    )

    result = await conn.execute(stmt)
    study = result.scalar_one_or_none()

    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    if not study.files:
        raise HTTPException(status_code=500, detail="Missing file upload data.")
    if not study.learning or not study.wait or not study.experiment:
        raise HTTPException(status_code=500, detail="Missing phase configuration.")
  

    return StudyConfigResponse(
        files=FileUploads(
            consent_form=study.files.consent_form,
            study_instruction=study.files.study_instructions,
            learning_image_list=study.files.learning_image_list,
            experiment_image_list=study.files.experiment_image_list,
            study_debrief=study.files.study_debrief,
        ),
        learning=LearningPhase(
            display_duration=study.learning.display_duration,
            pause_duration=study.learning.pause_duration,
            display_method=study.learning.display_method,
        ),
        wait=WaitPhase(
            display_duration=study.wait.display_duration,
        ),
        experiment=ExperimentPhase(
            display_duration=study.experiment.display_duration,
            pause_duration=study.experiment.pause_duration,
            display_method=study.experiment.display_method,
            response_method=study.experiment.response_method,
        ),
        conclusion=ConclusionPhase(
            show_results=study.conclusion.show_results,
            has_survey=study.conclusion.has_survey,
            questions=[question.text for question in study.demographics.questions] if study.conclusion.has_survey else None
        )
    )


async def get_survey_id(
        study_id:uuid.UUID, conn:AsyncSession        
) -> uuid.UUID:
    """Returns matching Survey ID from corresponding Study ID"""
    try:
        stmt = (
            select(UserSurveyConfig.id)
            .where(UserSurveyConfig.study_config_id == study_id)
        )
        result = await conn.execute(stmt)
        return result.scalar_one_or_none()
    
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    

async def get_survey_questions_from_db(
        survey_id:uuid.UUID, conn:AsyncSession
) -> SurveyQuestions:
    """Returns Survey Questions"""
    try:
        stmt = (
            select(SurveyQuestion.text)
            .where(SurveyQuestion.survey_config_id == survey_id)
        )
        result = await conn.execute(stmt)
        survey_questions = result.scalars().all()
        return SurveyQuestions(questions=survey_questions)

    except Exception as e:
        print(str(e))  
    
    