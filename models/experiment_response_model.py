import uuid
from sqlalchemy import Column, String, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from .base_model import Base

class ExperimentResponseModel(Base):
    __tablename__ = "experiment_responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_results_id = Column(UUID(as_uuid=True), ForeignKey("study_results.id"), nullable=False)
    image_id = Column(UUID(as_uuid=True), nullable=False)
    answer = Column(String, nullable=False)
    response_time = Column(Float, nullable=False) 