import uuid

from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import selectinload

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
from fastapi import HTTPException
from io import BytesIO
from schemas.study_config_response_schema import (
    StudyConfigResponse,
    FileUploads,
    LearningPhase,
    WaitPhase,
    ExperimentPhase,
    ConclusionPhase,
)

"""
Helper Functions to map incoming multipart/form-data
into their corresponding pydantic models.
This will help with database insertion and type enforcement.

Example async methods to show how to interact
with the database using SQLAlchemy
"""


async def get_study(study_id: uuid.UUID, conn: AsyncSession) -> StudyConfigResponse:
    stmt = (
        select(StudyConfiguration)
        .options(
            selectinload(StudyConfiguration.learning),
            selectinload(StudyConfiguration.wait),
            selectinload(StudyConfiguration.experiment),
            # selectinload(StudyConfiguration.survey),
            selectinload(StudyConfiguration.files),
            selectinload(StudyConfiguration.conclusion),
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
            has_survey=study.conclusion.survey,
        ),
    )


# INSERT
async def add_study(config: StudyConfigRequest, conn: AsyncSession):
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
        raise e


async def get_study_id_list(conn: AsyncSession):
    try:
        stmt = select(StudyConfiguration).execution_options(populate_existing=True)
        result = await conn.execute(stmt)
        ids: list[uuid.UUUID] = []
        rows = result.scalars().all()
        for study in rows:
            ids.append(study.id)
        return ids
    except Exception:
        raise HTTPException(404)


# async def get_uploaded_files(study_id: uuid.UUID, conn: AsyncSession):
#     try:
#         stmt = (
#             select(UploadedFiles)
#             .where(UploadedFiles.study_config_id == study_id)
#             .execution_options(populate_existing=True)
#         )
#         result = await conn.execute(stmt)
#         files = result.scalars().first()
#         if files.study_config_id != study_id:
#             raise HTTPException(status_code=404, detail="Invalid ID")
#         return FileUploads(
#             consent_form=FileData(filename=files.consent_form, data=files.consent_form_bytes),
#             study_instruction=FileData(filename=files.study_instruction, data=files.study_instruction_bytes),
#             learning_image_list=files.learning_image_list,
#             experiment_image_list=files.experiment_image_list,
#             study_debrief=FileData(filename=files.study_debrief, data=files.study_debrief)
#         )
#     except Exception as e:
#         raise HTTPException(status_code=404, detail=e)


async def get_consent_form(study_id: uuid.UUID, conn: AsyncSession):
    try:
        stmt = (
            select(UploadedFiles.consent_form, UploadedFiles.consent_form_bytes)
            .where(UploadedFiles.study_config_id == study_id)
            .execution_options(populate_existing=True)
        )
        result = await conn.execute(stmt)
        file = result.first()

        if not file:
            raise HTTPException(status_code=404, detail="Consent form not found")

        return StreamingResponse(
            BytesIO(file[1]),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'inline; filename="{file[0]}"'
            },
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=e)


"""
Adds the corresponding section to the database
"""


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
