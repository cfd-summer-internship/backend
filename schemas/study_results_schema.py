from pydantic import BaseModel
from uuid import UUID
from typing import List
from datetime import datetime

#NOT SURE IF USED?
class StudyResult(BaseModel):
    id: UUID
    study_id: UUID
    subject_id: UUID
    submitted: datetime

class ResponseIdentifiers(BaseModel):
    study_id: UUID
    config_id: UUID
    subject_id: UUID

class StudyResponseSchema(BaseModel):
    image_id: str
    answer: int
    response_time: float

class StudyResultsPayload(BaseModel):
    identity: ResponseIdentifiers
    responses: List[StudyResponseSchema]

#NOT SURE IF USED ANYWHERE
# class StudyResponseList(BaseModel):
#     responses: List[StudyResponseSchema]