from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from base import Base
import uuid
from study_config_model import StudyConfiguration
from survey_answers_model import SurveyAnswer
from survey_questions_model import SurveyQuestion


class DemographicSurvey(Base):
    __tablename__ = "survey_config"

    # SET UUID FOR ID
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True
    )

    # STUDY CONFIG ID (FK)
    study_config_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "study_config.id",
            ondelete="CASCADE",
            onupdate="CASCADE"),
        unique=True
    )

    # BI-DIRECTIONAL REFERENCE TO STUDY CONFIG
    study: Mapped[StudyConfiguration] = relationship(back_populates="survey")

    # BI-DIRECTIONAL REFERENCE TO SUVERY QUESTIONS
    questions: Mapped[list["SurveyQuestion"]] = relationship(back_populates="survey")

    # BI-DIRECTIONAL REFERENCE TO SUVERY QUESTIONS
    answers: Mapped[list["SurveyAnswer"]] = relationship(back_populates="survey")
