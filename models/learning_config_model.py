from sqlalchemy import Integer, Enum as SqlEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from models.base_model import Base
from .enums import DisplayMethodEnum
from models.study_config_model import StudyConfiguration


#LEARNING PHASE CONFIG
class LearningConfiguration(Base):
    __tablename__ ="learn_config"

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

    #PAUSE DURATION
    pause_duration:Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    #DISPLAY METHOD
    #Takes either RANDOM or SEQUENTIAL
    display_method:Mapped[DisplayMethodEnum] = mapped_column(
        SqlEnum(DisplayMethodEnum,
                name="display_method",
                native_enum=False),
        nullable=False
    )

    #REFERENCE TO STUDY CONFIG
    study : Mapped[StudyConfiguration]=relationship(back_populates="learning")
