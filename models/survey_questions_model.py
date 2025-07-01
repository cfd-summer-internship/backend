import uuid
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base_model import Base
from typing import TYPE_CHECKING

#That tells linters and type checkers:
# “Only import this when doing static analysis (e.g., by Ruff or MyPy), not at runtime.”

if TYPE_CHECKING:
    from demographics_survey_model import DemographicSurvey

class SurveyQuestion(Base):
    __tablename__ = "survey_question"

    id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        primary_key=True,
        autoincrement=True
    )

    survey_config_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("survey_config.id", ondelete="CASCADE", onupdate="CASCADE"),
        unique=True
    )

    text: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    survey: Mapped["DemographicSurvey"] = relationship("DemographicSurvey", back_populates="questions")
