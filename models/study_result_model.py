from datetime import datetime
from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, List, relationship
import uuid
from models.base_model import Base
from models.study_response_model import StudyResponse


class StudyResults(Base):
    __tablename__ = "study_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True
    )

    # STUDY ID (FK, 1:MANY)
    study_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("study.id", ondelete="CASCADE", onupdate="CASCADE"),
        unique=True,
    )

    subject_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), default=uuid.uuid4, unique=True
    )

    submitted = mapped_column(DateTime, default=datetime.datetime.utcnow)

    # REFERENCE TO STUDY REPONSES ONE-TO-MANY
    responses: Mapped[List[StudyResponse]] = relationship()
