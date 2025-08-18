import uuid
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base_model import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.user_survey_config_model import UserSurveyConfig


class SurveyAnswer(Base):
    __tablename__ = "survey_answer"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False
    )

    study_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    age: Mapped[str] = mapped_column(String, nullable=False)
    sex: Mapped[str] = mapped_column(String, nullable=False)
    race: Mapped[str] = mapped_column(String, nullable=False)

    #Removed REFERENCE TO SURVEY CONFIG (1:MANY)


    #Removed relationship with Survey Questions since we dont fetch it from db anymore
