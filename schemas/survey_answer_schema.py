from pydantic import BaseModel
from uuid import UUID

class SurveyAnswerResponse(BaseModel):
    study_id: UUID
    age: str
    sex: str
    race: str

