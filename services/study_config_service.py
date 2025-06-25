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
from schemas.study_config_schema import StudyConfig, LearningPhase, FileUploads, WaitPhase, ExperimentPhase, \
    ConclusionPhase
from fastapi import Form, UploadFile, File, Depends

"""
Helper Functions to map incoming multipart/form-data
into their corresponding pydantic models.
This will help with database insertion and type enforcement.

Example async methods to show how to interact
with the database using SQLAlchemy
"""

#SELECT
async def get_study(id: uuid.UUID, conn: AsyncSession):
    stmt = (
        select(StudyConfiguration)
        .options(
            selectinload(StudyConfiguration.learning),
            selectinload(StudyConfiguration.wait),
            selectinload(StudyConfiguration.experiment),
            selectinload(StudyConfiguration.survey),
            selectinload(StudyConfiguration.files)
    )
    .where(StudyConfiguration.id == id)
    )
    result = await conn.execute(stmt)
    study = result.scalars().first()
    return StudyConfig.model_validate(study)

#INSERT
async def add_study(config: StudyConfig, conn: AsyncSession):
    try:
        new_study = StudyConfiguration(
            show_results=config.conclusion_phase.show_results
        )
        conn.add(new_study)
        await conn.flush()  # To get new_study.id

        await save_file_uploads(new_study.id, config.file_uploads, conn)
        await save_learning_phase(new_study.id, config.learning_phase, conn)
        await save_wait_phase(new_study.id, config.wait_phase, conn)
        await save_experiment_phase(new_study.id, config.experiment_phase, conn)
        await save_conclusion_phase(new_study.id, config.conclusion_phase, conn)

        await conn.commit()
        return new_study.id

    except Exception as e:
        await conn.rollback()
        raise e



async def save_learning_phase(study_id, data: LearningPhase, conn):
    conn.add(LearningConfiguration(
        study_config_id=study_id,
        display_duration=data.display_duration,
        pause_duration=data.pause_duration,
        display_method=data.display_method
    ))

async def save_wait_phase(study_id, data: WaitPhase, conn):
    conn.add(WaitingConfiguration(
        study_config_id=study_id,
        display_duration=data.display_duration
    ))

async def save_experiment_phase(study_id, data: ExperimentPhase, conn):
    conn.add(ExperimentConfiguration(
        study_config_id=study_id,
        display_duration=data.display_duration,
        pause_duration=data.pause_duration,
        display_method=data.display_method,
        response_method=data.answer_method
    ))

async def save_conclusion_phase(study_id, data: ConclusionPhase, conn):
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





async def save_file_uploads(study_id, files: FileUploads, conn):
    conn.add(UploadedFiles(
        study_config_id=study_id,
        consent_form=files.consent_form.filename,
        instruction_set=files.study_instructions.filename,
        learning_image_list=files.learning_phase_list.filename,
        experiment_image_list=files.experiment_phase_list.filename
    ))





# ------ Form Parsers -------

def getLearningPhase(
        displayDuration:int = Form(...,alias="learning.displayDuration"), #(...)
        pauseDuration:int = Form(...,alias="learning.pauseDuration"),
        displayMethod:DisplayMethodEnum = Form(...,alias="learning.displayMethod")
):
    return LearningPhase(
        display_duration=displayDuration,
        pause_duration=pauseDuration,
        display_method=displayMethod
    )

def getWaitPhase(
        DisplayDuration:int = Form(...,alias="waiting.displayDuration"),
): return WaitPhase(
       wait_phase=DisplayDuration
    )

def getExperimentPhase(
    displayDuration: int = Form(..., alias="experiment.displayDuration"),
    pauseDuration: int = Form(..., alias="experiment.pauseDuration"),
    displayMethod: DisplayMethodEnum = Form(..., alias="experiment.displayMethod"),
    responseMethod: ResponseMethodEnum = Form(..., alias="experiment.responseMethod")
):
    return ExperimentPhase(
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
    return ConclusionPhase(
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
    return FileUploads(
        consent_form=consentForm,
        study_instructions=studyInstructions,
        learning_phase_list=learningList,
        experiment_phase_list=experimentList
    )

def parse_study_form(
    learning: LearningPhase = Depends(getLearningPhase),
    waiting: WaitPhase = Depends(getWaitPhase),
    experiment: ExperimentPhase = Depends(getExperimentPhase),
    conclusion: ConclusionPhase = Depends(getConclusionPhase),
    files: FileUploads = Depends(getFileUploads)
) -> StudyConfig:
    return StudyConfig(
        learning_phase=learning,
        wait_phase=waiting,
        experiment_phase=experiment,
        conclusion_phase=conclusion,
        file_uploads=files
    )

