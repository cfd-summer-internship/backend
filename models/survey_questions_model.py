import uuid
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base_model import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.user_survey_config_model import UserSurveyConfig
    from models.survey_answers_model import SurveyAnswer

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
        primary_key=True
    )

    text: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    #REFERENCE TO SURVEY CONFIG 1:MANY
    survey: Mapped["UserSurveyConfig"] = relationship(back_populates="questions")

    #REFERENCE TO SURVEY ANSWER (1:1)
    answer: Mapped["SurveyAnswer"] = relationship(back_populates="question")
