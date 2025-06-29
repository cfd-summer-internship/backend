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
    debrief_file: UploadFile
    has_survey: bool


class FileUploadsRequest(BaseModel):
    consent_form: UploadFile
    study_instructions: UploadFile
    learning_phase_list: UploadFile
    experiment_phase_list: UploadFile


class StudyConfigRequest(BaseModel):
    files: FileUploadsRequest
    learning: LearningPhaseRequest
    wait: WaitPhaseRequest
    experiment: ExperimentPhaseRequest
    survey: ConclusionPhaseRequest  # or 'survey' if you're storing demographic survey

    model_config = ConfigDict(from_attributes=True)
