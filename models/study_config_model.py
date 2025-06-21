from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from .base import Base



class StudyConfiguration(Base):
    __tablename__ = "study_config"

    #SET UUID FOR ID and PK
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True
    )

    #SHOW USER RESULTS
    show_results:Mapped[Boolean]= mapped_column(
        Boolean,
        nullable=False
    )

    #FK TO USER ID
    # researcher_id:Mapped[String]=mapped_column(
    #     String,
    #     ForeignKey(
    #         "researcher.id",
    #         ondelete="CASCADE",
    #         onupdate="CASCADE",
    #     ),
    #     nullable=False
    # )

    #REFERENCE TO LEARNING CONFIG
    learning:Mapped["LearningConfiguration"]=relationship(
        back_populates="study",
        cascade="all, delete-orphan",
        uselist=False
    )

    #REFERENCE TO LEARNING CONFIG
    wait:Mapped["WaitingConfiguration"]=relationship(
        back_populates="study",
        cascade="all, delete-orphan",
        uselist=False
    )

    #REFERENCE TO LEARNING CONFIG
    experiment:Mapped["ExperimentConfiguration"]=relationship(
        back_populates="study",
        cascade="all, delete-orphan",
        uselist=False
    )

    #REFERENCE TO LEARNING CONFIG
    files:Mapped["UploadedFiles"]=relationship(
        back_populates="study",
        cascade="all, delete-orphan",
        uselist=False
    )

    #REFERENCE TO LEARNING CONFIG
    survey:Mapped["DemographicSurvey"]=relationship(
        back_populates="study",
        cascade="all, delete-orphan",
        uselist=False
    )