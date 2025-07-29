from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
import uuid
from models.base_model import Base


class StudyResponse(Base):
    __tablename__ = "study_response"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    # STUDY RESULTS ID (FK, 1:MANY)
    study_results_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("study_results.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True
    )

    image_id: Mapped[str] = mapped_column(String, nullable=False)

    response_time: Mapped[float] = mapped_column(Float, nullable=False)

    answer: Mapped[int] = mapped_column(Integer, nullable=False)


