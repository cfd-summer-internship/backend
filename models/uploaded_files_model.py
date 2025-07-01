import uuid

from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, BYTEA
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base_model import Base
from .study_config_model import StudyConfiguration


class UploadedFiles(Base):
    __tablename__="files_config"

    #STUDY CONFIG ID (FK,PK)
    study_config_id:Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "study_config.id",
            ondelete="CASCADE",
            onupdate="CASCADE"),
        primary_key=True,
        unique=True
    )

    consent_form:Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    consent_form_bytes:Mapped[BYTEA] = mapped_column(
        BYTEA,
        nullable=False
    )    

    learning_image_list:Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    experiment_image_list:Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    study_instructions:Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    study_instructions_bytes:Mapped[BYTEA] = mapped_column(
        BYTEA,
        nullable=False
    )    

    study_debrief:Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    study_debrief_bytes:Mapped[BYTEA] = mapped_column(
        BYTEA,
        nullable=False
    )    



    #REFERENCE TO STUDY CONFIG
    study : Mapped[StudyConfiguration]=relationship(back_populates="files")

