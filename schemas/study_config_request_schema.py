from fastapi import UploadFile
from pydantic import BaseModel, ConfigDict

from models.enums import DisplayMethodEnum, ResponseMethodEnum

"""
These models help with type enforcement
and structure the incoming data
to match the database data types
and columns for each corresponding
table.
"""


class LearningPhaseRequest(BaseModel):
    display_duration: int
    pause_duration: int
    display_method: DisplayMethodEnum


class WaitPhaseRequest(BaseModel):
    display_duration: int


class ExperimentPhaseRequest(LearningPhaseRequest):
    response_method: ResponseMethodEnum


class ConclusionPhaseRequest(BaseModel):
    show_results: bool
    has_survey: bool


class FileUploadsRequest(BaseModel):
    consent_form: UploadFile #PDF
    study_instructions: UploadFile #PDF
    learning_phase_list: UploadFile #CSV
    experiment_phase_list: UploadFile #CSV
    study_debrief: UploadFile #PDF


class StudyConfigRequest(BaseModel):
    files: FileUploadsRequest
    learning: LearningPhaseRequest
    wait: WaitPhaseRequest
    experiment: ExperimentPhaseRequest
    conclusion: ConclusionPhaseRequest

    model_config = ConfigDict(from_attributes=True)
