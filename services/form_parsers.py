from typing import Optional
from models.enums import DisplayMethodEnum, ResponseMethodEnum
from schemas.study_config_request_schema import LearningPhaseRequest, FileUploadsRequest, WaitPhaseRequest, ExperimentPhaseRequest, \
    ConclusionPhaseRequest
from fastapi import Form, UploadFile, File

# ------ Form Parsers -------


def get_learning_phase(
        displayDuration: int = Form(..., alias="learning.displayDuration"),  #(...)
        pauseDuration: int = Form(..., alias="learning.pauseDuration"),
        displayMethod: DisplayMethodEnum = Form(..., alias="learning.displayMethod")
):
    return LearningPhaseRequest(
        display_duration=displayDuration,
        pause_duration=pauseDuration,
        display_method=displayMethod
    )


def get_wait_phase(
        DisplayDuration: int = Form(..., alias="waiting.displayDuration"),
): return WaitPhaseRequest(
    display_duration=DisplayDuration
)


def get_experiment_phase(
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


def get_conclusion_phase(
        survey: bool = Form(..., alias="conclusion.survey"),
):
    return ConclusionPhaseRequest(
        has_survey=survey
    )


def get_file_uploads(
        consentForm: UploadFile = File(..., alias="configFiles.consentForm"),
        studyInstructions: UploadFile = File(..., alias="configFiles.studyInstructions"),
        learningList: UploadFile = File(..., alias="configFiles.learningList"),
        experimentList: UploadFile = File(..., alias="configFiles.experimentList"),
        studyDebrief: Optional[UploadFile] = File(None, alias="configFiles.studyDebrief"),
):
    return FileUploadsRequest(
        consent_form=consentForm,#file_validator.validate_file_type(consentForm),
        study_instructions=studyInstructions,#file_validator.validate_file_type(studyInstructions),
        learning_phase_list=learningList,
        experiment_phase_list=experimentList,
        study_debrief=studyDebrief#file_validator.validate_file_type(studyDebrief)
    )