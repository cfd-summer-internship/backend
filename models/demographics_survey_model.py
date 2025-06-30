import uuid
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base_model import Base
from models.study_config_model import StudyConfiguration


class DemographicSurvey(Base):
    __tablename__ = "survey_config"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True
    )

    study_config_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("study_config.id", ondelete="CASCADE", onupdate="CASCADE"),
        unique=True
    )

    study: Mapped[StudyConfiguration] = relationship(back_populates="survey")


# ✅ Delay the relationships — no import needed
DemographicSurvey.questions = relationship("SurveyQuestion", back_populates="survey")
DemographicSurvey.answers = relationship("SurveyAnswer", back_populates="survey")
