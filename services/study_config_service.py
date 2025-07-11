import uuid

from fastapi import HTTPException

from models.conclusion_config_model import ConclusionConfiguration
from models.study_config_model import StudyConfiguration
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
    ConclusionPhaseRequest,
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
        new_study = StudyConfiguration()
        conn.add(new_study)
        await conn.flush()  # To get new_study.id

        await save_file_uploads(new_study.id, config.files, conn)
        await save_learning_phase(new_study.id, config.learning, conn)
        await save_wait_phase(new_study.id, config.wait, conn)
        await save_experiment_phase(new_study.id, config.experiment, conn)
        await save_conclusion_phase(new_study.id, config.conclusion, conn)

        await conn.commit()
        return new_study.id

    except Exception as e:
        await conn.rollback()
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
            survey=data.has_survey,
        )
    )


async def save_file_uploads(study_id: uuid.UUID, files: FileUploadsRequest, conn):
    """Inserts Files into database.

    Saves the filename as well as the raw file bytes as a BYTEA datatype."""
    conn.add(
        UploadedFiles(
            study_config_id=study_id,
            consent_form=files.consent_form.filename,
            consent_form_bytes=await files.consent_form.read(),
            study_instructions=files.study_instructions.filename,
            study_instructions_bytes=await files.study_instructions.read(),
            learning_image_list=files.learning_phase_list.filename,
            experiment_image_list=files.experiment_phase_list.filename,
            study_debrief=files.study_debrief.filename,
            study_debrief_bytes=await files.study_debrief.read(),
        )
    )
