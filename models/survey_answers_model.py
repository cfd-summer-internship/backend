import uuid
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base_model import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.user_survey_config_model import UserSurveyConfig


class SurveyAnswer(Base):
    __tablename__ = "survey_answer"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False
    )

    survey_config_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("survey_config.id", ondelete="CASCADE", onupdate="CASCADE"),
        unique=True
    )

    survey_question_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("survey_question.id", ondelete="CASCADE", onupdate="CASCADE"),
        unique=True
    )

    text: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    #REFERENCE TO SURVEY QUESTION (1:1)
    question: Mapped["UserSurveyConfig"] = relationship(back_populates="answer")

    #REFERENCE TO SURVEY CONFIG (1:MANY)
    survey: Mapped["UserSurveyConfig"] = relationship(back_populates="answers")
