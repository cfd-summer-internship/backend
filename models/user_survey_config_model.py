from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from models.base_model import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.study_config_model import StudyConfiguration


#LEARNING PHASE CONFIG
class UserSurveyConfig(Base):
    __tablename__ ="survey_config"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True
    )

    #STUDY CONFIG ID (FK)
    study_config_id:Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "study_config.id",
            ondelete="CASCADE",
            onupdate="CASCADE"),
        unique=True
    )

    #REFERENCE TO STUDY CONFIG
    study : Mapped["StudyConfiguration"]=relationship(back_populates="demographics")