from pydantic import BaseModel
from uuid import UUID

class SurveyAnswerResponse(BaseModel):
    study_id: UUID
    age: int
    sex: str
    race: str