from pydantic import BaseModel, ConfigDict
from models.enums import DisplayMethodEnum, ResponseMethodEnum


class LearningPhase(BaseModel):
    display_duration: int
    pause_duration: int
    display_method: DisplayMethodEnum
    model_config = ConfigDict(from_attributes=True)


class WaitPhase(BaseModel):
    display_duration: int
    model_config = ConfigDict(from_attributes=True)


class ExperimentPhase(LearningPhase):
    response_method: ResponseMethodEnum
    model_config = ConfigDict(from_attributes=True)


class ConclusionPhase(BaseModel):
    show_results: bool
    debrief_file: str
    has_survey: bool

    model_config = ConfigDict(from_attributes=True)



class FileUploads(BaseModel):
    consent_form: str
    instruction_set: str
    learning_image_list: str
    experiment_image_list: str
    model_config = ConfigDict(from_attributes=True)



class StudyConfigResponse(BaseModel):
    files: FileUploads
    learning: LearningPhase
    wait: WaitPhase
    experiment: ExperimentPhase
    survey: ConclusionPhase
    model_config = ConfigDict(from_attributes=True)
