from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict

class StudyListItem(BaseModel):
    id: UUID
    configuration_id: UUID
    total_submissions: int
    expected_items: int
    last_submission_at: Optional[datetime] = None

class StudyListResponse(BaseModel):
    items: List[StudyListItem]

class StudySummary(BaseModel):
    study_id: UUID
    total_submissions: int
    expected_items: int
    complete_submissions: int
    completion_rate: float
    avg_response_time_ms: Optional[float] = None
    answer_histogram: Dict[int, int]  # answer -> count

class ResultRow(BaseModel):
    study_results_id: UUID
    subject_id: UUID
    submitted: datetime
    responses: List[Dict]  # {image_id, answer, response_time}

class PagedResults(BaseModel):
    items: List[ResultRow]
    page: int
    page_size: int
    total: int

class StudyResultsSchema(BaseModel):
    id: UUID
    study_id: UUID
    config_id: UUID
    subject_id: UUID
    submitted: datetime

class StudyResponseSchema(BaseModel):
    image_id: str
    answer: int
    response_time: float

class SurveyAnswerSchema(BaseModel):
    subject_id: UUID
    age: int
    sex: str
    race: str

class ResultsExportSchema(BaseModel):
    results: StudyResultsSchema
    responses: list[StudyResponseSchema]
    demographics: Optional[SurveyAnswerSchema] = None