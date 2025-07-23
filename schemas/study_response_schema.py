from pydantic import BaseModel
from uuid import UUID
from typing import List

class ExperimentResponse(BaseModel):
    image_id: UUID
    answer: str
    response_time: float

class ExperimentResponseList(BaseModel):
    responses: List[ExperimentResponse]