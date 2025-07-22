from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from models.base_model import Base
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from models.user_survey_config_model import UserSurveyConfig
    from models.learning_config_model import LearningConfiguration
    from models.waiting_config_model import WaitingConfiguration
    from models.experiment_config_model import ExperimentConfiguration
    from models.uploaded_files_model import UploadedFiles
    from models.conclusion_config_model import ConclusionConfiguration
    from models.study_model import Study


class StudyConfiguration(Base):
    __tablename__ = "study_config"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True
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

    conclusion: Mapped["ConclusionConfiguration"] = relationship(
        back_populates="study",
        cascade="all, delete-orphan",
        uselist=False
    )
 
    demographics: Mapped["UserSurveyConfig"] = relationship(
        back_populates="study",
        cascade="all, delete-orphan",
        uselist=False
    )

    #STUDY PARENT -> STORES INFORMATION REGARDING THE STUDY
    study: Mapped["Study"] = relationship(
        back_populates="config",
        cascade="all, delete-orphan",
        uselist=False
    )
