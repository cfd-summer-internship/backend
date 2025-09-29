from pydantic import BaseModel
from uuid import UUID

class SurveyAnswerResponse(BaseModel):
    subject_id: UUID
    age: int
    sex: str
    race: str
    