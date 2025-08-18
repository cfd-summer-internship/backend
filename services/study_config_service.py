import uuid
import csv
from fastapi import HTTPException, UploadFile

from models.conclusion_config_model import ConclusionConfiguration
from models.study_config_model import StudyConfiguration
from models.study_model import Study
from models.user_survey_config_model import UserSurveyConfig
from sqlalchemy.ext.asyncio import AsyncSession

from models.experiment_config_model import ExperimentConfiguration
from models.learning_config_model import LearningConfiguration
from models.uploaded_files_model import UploadedFiles
from models.waiting_config_model import WaitingConfiguration
from schemas.study_config_request_schema import (
    StudyConfigRequest,
    LearningPhaseRequest,
    FileUploadsRequest,
    WaitPhaseRequest,
    ExperimentPhaseRequest,
    ConclusionPhaseRequest
)


async def add_study(config: StudyConfigRequest, conn: AsyncSession):
    """Adds a new Study Configuration into the database

    Uses helper functions to handle insertion of specific components.
    Only Commits changes if the entire configuration was succesfully inserted.
    Rollsback uncommited changes on failed insert.

    Raises:
        HTTPException: 500: Exception Details
    """
    try:
        study_id = uuid.uuid4()
        config_id = uuid.uuid4()
        study = Study(id=study_id, configuration_id=config_id, researcher=config.researcher)
        conn.add(study)

        study_config = StudyConfiguration(id=config_id)
        conn.add(study_config)
        #await conn.flush()  # To get study_config.id

        await save_file_uploads(study_config.id, config.files, conn)
        await save_learning_phase(study_config.id, config.learning, conn)
        await save_wait_phase(study_config.id, config.wait, conn)
        await save_experiment_phase(study_config.id, config.experiment, conn)
        await save_conclusion_phase(study_config.id, config.conclusion, conn)
       
        if config.conclusion.has_survey:
            survey_id = uuid.uuid4() #generate UUID
            await save_user_survey(survey_id,study_config.id, conn)
       
        await conn.commit()
        study_code = str(study_config.id)[-6:] #TODO: Change to Study ID and update all calls for a study ID
        return study_code

    except Exception as e:
        await conn.rollback()
        print("Insertion Error: ",str(e))
        raise HTTPException(500, detail=str(e))


# HELPER FUNCTIONS FOR DATABASE INSERTION
async def save_learning_phase(
    study_id: uuid.UUID, data: LearningPhaseRequest, conn: AsyncSession
):
    conn.add(
        LearningConfiguration(
            study_config_id=study_id,
            display_duration=data.display_duration,
            pause_duration=data.pause_duration,
            display_method=data.display_method,
        )
    )


async def save_wait_phase(
    study_id: uuid.UUID, data: WaitPhaseRequest, conn: AsyncSession
):
    conn.add(
        WaitingConfiguration(
            study_config_id=study_id, display_duration=data.display_duration
        )
    )


async def save_experiment_phase(
    study_id: uuid.UUID, data: ExperimentPhaseRequest, conn: AsyncSession
):
    conn.add(
        ExperimentConfiguration(
            study_config_id=study_id,
            display_duration=data.display_duration,
            pause_duration=data.pause_duration,
            display_method=data.display_method,
            response_method=data.response_method,
        )
    )


async def save_conclusion_phase(
    study_id: uuid.UUID, data: ConclusionPhaseRequest, conn: AsyncSession
):
    conn.add(
        ConclusionConfiguration(
            study_config_id=study_id,
            show_results=data.show_results,
            has_survey=data.has_survey,
        )
    )


async def save_user_survey(
    survey_id: uuid.UUID, study_id: uuid.UUID, conn: AsyncSession):
    """Inserts User Survey Config into database"""
    conn.add(
        UserSurveyConfig(
            id = survey_id,
            study_config_id=study_id)
        )


async def save_file_uploads(study_id: uuid.UUID, files: FileUploadsRequest, conn: AsyncSession):
    """Inserts Files into database.

    Saves the filename as well as the raw file bytes as a BYTEA datatype."""
    conn.add(
        UploadedFiles(
            study_config_id=study_id,
            consent_form=files.consent_form.filename,
            consent_form_bytes=await files.consent_form.read(),
            study_instructions=files.study_instructions.filename,
            study_instructions_bytes=await files.study_instructions.read(),
            learning_image_list=await extract_from_csv(files.learning_phase_list),
            experiment_image_list=await extract_from_csv(files.experiment_phase_list),
            study_debrief=files.study_debrief.filename if files.study_debrief else None,
            study_debrief_bytes=await files.study_debrief.read() if files.study_debrief else None,
        )
    )

#PERHAPS USE ONE FILE INSTEAD OF TWO AND A FLAG TO INDICATE WHAT TYPE IT IS
#THEN EXTRACT BASED OFF OF THE ROW?
async def extract_from_csv(file: UploadFile):
    """Extracts a list of strings from an uploaded csv file"""
    content = await file.read()
    lines = content.decode("utf-8").splitlines()
    reader = csv.reader(lines)
    image_list:list[str]=[]
    for row in reader:
        if row:
            image_list.extend(row)

    return image_list

    
