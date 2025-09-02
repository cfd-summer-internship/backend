from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from models.enums import DisplayMethodEnum, ResponseMethodEnum


class MessageResponse(BaseModel):
    message: str

class StudyCodeReponse(BaseModel):
    study_code:str

class LearningPhase(BaseModel):
    display_duration: int
    pause_duration: int
    display_method: DisplayMethodEnum
    image_ids: Optional[list[str]] = None
    images: list[str]
    model_config = ConfigDict(from_attributes=True)


class WaitPhase(BaseModel):
    display_duration: int
    model_config = ConfigDict(from_attributes=True)


class ExperimentPhase(LearningPhase):
    response_method: ResponseMethodEnum
    model_config = ConfigDict(from_attributes=True)


class SurveyQuestions(BaseModel):
    questions: list[str]
    model_config = ConfigDict(from_attributes=True)


class ConclusionPhase(BaseModel):
    show_results: bool
    has_survey: bool
    questions: Optional[list[str]] = None

    model_config = ConfigDict(from_attributes=True)


class FileUploads(BaseModel):
    consent_form: str
    study_instruction: str
    study_debrief: Optional[str]
    model_config = ConfigDict(from_attributes=True)


class StudyConfigResponse(BaseModel):
    files: FileUploads
    learning: LearningPhase
    wait: WaitPhase
    experiment: ExperimentPhase
    conclusion: ConclusionPhase
    model_config = ConfigDict(from_attributes=True)


class ResearcherConfigResponse(BaseModel):
    researcher_id: UUID
    config_ids: List[UUID]
    model_config = ConfigDict(from_attributes=True)