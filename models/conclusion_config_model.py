import uuid

from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base_model import Base
from models.study_config_model import StudyConfiguration


class ConclusionConfiguration(Base):
    __tablename__ ="conclusion_config"

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

    show_results: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False
    )

    survey: Mapped[bool] = mapped_column(
        Boolean,
        nullable=True
    )

    #REFERENCE TO STUDY CONFIG
    study : Mapped[StudyConfiguration]=relationship(back_populates="conclusion")

