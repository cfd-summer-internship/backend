import uuid

from sqlalchemy import select, update  # , joinedload,selectinload
from sqlalchemy.orm import selectinload

from models.enums import DisplayMethodEnum, ResponseMethodEnum
from models.study_config_model import StudyConfiguration
from sqlalchemy.ext.asyncio import AsyncSession

from models.demographics_survey_model import DemographicSurvey
from models.experiment_config_model import ExperimentConfiguration
from models.learning_config_model import LearningConfiguration
from models.uploaded_files_model import UploadedFiles
from models.waiting_config_model import WaitingConfiguration
from schemas.study_config_request_schema import StudyConfigRequest, LearningPhaseRequest, FileUploadsRequest, WaitPhaseRequest, ExperimentPhaseRequest, \
    ConclusionPhaseRequest
from fastapi import Form, UploadFile, File, HTTPException

from schemas.study_config_response_schema import StudyConfigResponse, FileUploads, LearningPhase, WaitPhase, \
    ExperimentPhase, ConclusionPhase

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
            selectinload(StudyConfiguration.survey),
            selectinload(StudyConfiguration.files),
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
            instruction_set=study.files.instruction_set,
            learning_image_list=study.files.learning_image_list,
            experiment_image_list=study.files.experiment_image_list,
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
        survey=ConclusionPhase(
            show_results=study.show_results,
            debrief_file=study.files.debrief or "",
            has_survey=bool(study.survey)
        )
    )






# INSERT
async def add_study(config: StudyConfigRequest, conn: AsyncSession):
    try:
        new_study = StudyConfiguration(
            show_results=config.survey.show_results
        )
        conn.add(new_study)
        await conn.flush()  # To get new_study.id

        await save_file_uploads(new_study.id, config.files, conn)
        await save_learning_phase(new_study.id, config.learning, conn)
        await save_wait_phase(new_study.id, config.wait, conn)
        await save_experiment_phase(new_study.id, config.experiment, conn)
        await save_conclusion_phase(new_study.id, config.survey, conn)

        await conn.commit()
        return new_study.id

    except Exception as e:
        await conn.rollback()
        raise e



async def save_learning_phase(study_id, data: LearningPhaseRequest, conn):
    conn.add(LearningConfiguration(
        study_config_id=study_id,
        display_duration=data.display_duration,
        pause_duration=data.pause_duration,
        display_method=data.display_method
    ))


async def save_wait_phase(study_id, data: WaitPhaseRequest, conn):
    conn.add(WaitingConfiguration(
        study_config_id=study_id,
        display_duration=data.display_duration
    ))


async def save_experiment_phase(study_id, data: ExperimentPhaseRequest, conn):
    conn.add(ExperimentConfiguration(
        study_config_id=study_id,
        display_duration=data.display_duration,
        pause_duration=data.pause_duration,
        display_method=data.display_method,
        response_method=data.response_method
    ))


async def save_conclusion_phase(study_id, data: ConclusionPhaseRequest, conn):
    # Update StudyConfiguration (only show_results here)
    await conn.execute(
        update(StudyConfiguration)
        .where(StudyConfiguration.id == study_id)
        .values(show_results=data.show_results)
    )

    # Add demographic survey row if requested
    if data.has_survey:
        conn.add(DemographicSurvey(study_config_id=study_id))

    # Update existing UploadedFiles row with debrief filename
    await conn.execute(
        update(UploadedFiles)
        .where(UploadedFiles.study_config_id == study_id)
        .values(debrief=data.debrief_file.filename)
    )


async def save_file_uploads(study_id, files: FileUploadsRequest, conn):
    conn.add(UploadedFiles(
        study_config_id=study_id,
        consent_form=files.consent_form.filename,
        instruction_set=files.study_instructions.filename,
        learning_image_list=files.learning_phase_list.filename,
        experiment_image_list=files.experiment_phase_list.filename
    ))


# ------ Form Parsers -------

def getLearningPhase(
        displayDuration: int = Form(..., alias="learning.displayDuration"),  #(...)
        pauseDuration: int = Form(..., alias="learning.pauseDuration"),
        displayMethod: DisplayMethodEnum = Form(..., alias="learning.displayMethod")
):
    return LearningPhaseRequest(
        display_duration=displayDuration,
        pause_duration=pauseDuration,
        display_method=displayMethod
    )


def getWaitPhase(
        DisplayDuration: int = Form(..., alias="waiting.displayDuration"),
): return WaitPhaseRequest(
    display_duration=DisplayDuration
)


def getExperimentPhase(
        displayDuration: int = Form(..., alias="experiment.displayDuration"),
        pauseDuration: int = Form(..., alias="experiment.pauseDuration"),
        displayMethod: DisplayMethodEnum = Form(..., alias="experiment.displayMethod"),
        responseMethod: ResponseMethodEnum = Form(..., alias="experiment.responseMethod")
):
    return ExperimentPhaseRequest(
        display_duration=displayDuration,
        pause_duration=pauseDuration,
        display_method=displayMethod,
        response_method=responseMethod
    )


def getConclusionPhase(
        showResults: bool = Form(..., alias="conclusion.showResults"),
        debrief: UploadFile = File(..., alias="conclusion.debrief"),
        survey: bool = Form(..., alias="conclusion.survey")
):
    return ConclusionPhaseRequest(
        show_results=showResults,
        debrief_file=debrief,
        has_survey=survey
    )


def getFileUploads(
        consentForm: UploadFile = File(..., alias="configFiles.consentForm"),
        studyInstructions: UploadFile = File(..., alias="configFiles.studyInstructions"),
        learningList: UploadFile = File(..., alias="configFiles.learningList"),
        experimentList: UploadFile = File(..., alias="configFiles.experimentList")
):
    return FileUploadsRequest(
        consent_form=consentForm,
        study_instructions=studyInstructions,
        learning_phase_list=learningList,
        experiment_phase_list=experimentList
    )