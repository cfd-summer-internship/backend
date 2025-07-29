from pydantic import BaseModel
from uuid import UUID
from typing import List
from datetime import datetime

class StudyResult(BaseModel):
    id: UUID
    study_id: UUID
    subject_id: UUID
    submitted: datetime

class StudyResponseSchema(BaseModel):
    image_id: str
    answer: int
    response_time: float

class StudyResponseList(BaseModel):
    responses: List[StudyResponseSchema]