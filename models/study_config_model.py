from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from models.base_model import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.learning_config_model import LearningConfiguration
    from models.waiting_config_model import WaitingConfiguration
    from models.experiment_config_model import ExperimentConfiguration
    from models.uploaded_files_model import UploadedFiles
    from models.demographics_survey_model import DemographicSurvey


class StudyConfiguration(Base):
    __tablename__ = "study_config"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True
    )

    show_results: Mapped[Boolean] = mapped_column(
        Boolean,
        nullable=False
    )

    learning: Mapped["LearningConfiguration"] = relationship(
        back_populates="study",
        cascade="all, delete-orphan",
        uselist=False
    )

    wait: Mapped["WaitingConfiguration"] = relationship(
        back_populates="study",
        cascade="all, delete-orphan",
        uselist=False
    )

    experiment: Mapped["ExperimentConfiguration"] = relationship(
        back_populates="study",
        cascade="all, delete-orphan",
        uselist=False
    )

    files: Mapped["UploadedFiles"] = relationship(
        back_populates="study",
        cascade="all, delete-orphan",
        uselist=False
    )

    survey: Mapped["DemographicSurvey"] = relationship(
        back_populates="study",
        cascade="all, delete-orphan",
        uselist=False
    )
