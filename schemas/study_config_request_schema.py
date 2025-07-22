from fastapi import UploadFile
from pydantic import BaseModel, ConfigDict
from typing import Optional

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


class SurveyQuestionsRequest(BaseModel):
    survey_questions: list[str]


class ConclusionPhaseRequest(BaseModel):
    show_results: bool
    has_survey: bool
    questions: Optional[list[str]] = None   


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
