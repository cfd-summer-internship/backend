import uuid
from sqlalchemy import ForeignKeyConstraint, Integer, PrimaryKeyConstraint, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base_model import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.user_survey_config_model import UserSurveyConfig
    from models.survey_questions_model import SurveyQuestion


class SurveyAnswer(Base):
    __tablename__ = "survey_answer"

    id: Mapped[int] = mapped_column(
        Integer
    )

    survey_config_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
    )

    survey_question_id: Mapped[int] = mapped_column(
        Integer,
    )

    text: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    __table_args__=(
        PrimaryKeyConstraint("survey_config_id","survey_question_id","id"),
        ForeignKeyConstraint(
            ["survey_config_id"],
            ["survey_config.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="survey_answer_survey_config_id_fkey"
        ),
        ForeignKeyConstraint(
            ["survey_config_id", "survey_question_id"],
            ["survey_question.survey_config_id", "survey_question.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="survey_answer_survey_question_id_fkey"
        ),
    )

    #REFERENCE TO SURVEY CONFIG (1:MANY)
    survey: Mapped["UserSurveyConfig"] = relationship(back_populates="answers")

    #REFERENCE TO SURVEY QUESTION (1:1)
    question: Mapped["SurveyQuestion"] = relationship(back_populates="answer")
