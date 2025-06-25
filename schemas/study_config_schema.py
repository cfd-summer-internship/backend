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


class LearningPhase(BaseModel):
    display_duration: int
    pause_duration: int
    display_method: DisplayMethodEnum


class WaitPhase(BaseModel):
    display_duration: int


class ExperimentPhase(LearningPhase):
    response_method: ResponseMethodEnum


class ConclusionPhase(BaseModel):
    show_results: bool
    debrief_file: UploadFile
    has_survey: bool


class FileUploads(BaseModel):
    consent_form: UploadFile
    study_instructions: UploadFile
    learning_phase_list: UploadFile
    experiment_phase_list: UploadFile


class StudyConfig(BaseModel):
    file_uploads: FileUploads
    learning_phase: LearningPhase
    wait_phase: WaitPhase
    experiment_phase: ExperimentPhase
    conclusion_phase: ConclusionPhase
    model_config = ConfigDict(from_attributes=True)
