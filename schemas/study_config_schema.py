from fastapi import UploadFile
from pydantic import BaseModel
"""
These models help with type enforcement
and structure the incoming data
to match the database data types
and columns for each corresponding
table.
"""
class LearningPhase(BaseModel):
    display_duration:int
    pause_duration:int
    display_method:str

class WaitPhase(BaseModel):
    wait_phase:int

class ExperimentPhase(LearningPhase):
    answer_method:str

class FileUploads(BaseModel):
    consent_form:UploadFile
    study_instructions:UploadFile