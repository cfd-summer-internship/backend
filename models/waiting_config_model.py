import uuid

from sqlalchemy import Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base_model import Base
from .study_config_model import StudyConfiguration


class WaitingConfiguration(Base):
    __tablename__ ="wait_config"

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

    #DISPLAY DURATION
    display_duration:Mapped[int]= mapped_column(
        Integer,
        nullable=False
    )

    #REFERENCE TO STUDY CONFIG
    study : Mapped[StudyConfiguration]=relationship(back_populates="wait")

