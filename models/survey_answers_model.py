import uuid

from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base_model import Base
from .demographics_survey_model import DemographicSurvey


class SurveyAnswer (Base):
    __tablename__ ="survey_answer"

    id:Mapped[Integer]=mapped_column(
        Integer,
        nullable=False,
        primary_key=True,
        autoincrement=True
    )

    #SURVEY ID (PK,FK)
    survey_config_id:Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "survey_config.id",
            ondelete="CASCADE",
            onupdate="CASCADE"),
            unique=True
    )

    text:Mapped[String] = mapped_column(
        String,
        nullable=False
    )

    #REFERENCE TO STUDY CONFIG
    survey : Mapped[DemographicSurvey]=relationship(back_populates="answers")