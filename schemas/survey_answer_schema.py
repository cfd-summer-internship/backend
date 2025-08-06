from pydantic import BaseModel
from uuid import UUID

class SurveyAnswerCreate(BaseModel):
    survey_config_id: UUID
    survey_question_id: int
    text: str
