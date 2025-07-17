import uuid
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base_model import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.user_survey_config_model import UserSurveyConfig

class SurveyQuestion(Base):
    __tablename__ = "survey_question"

    id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        primary_key=True,
        autoincrement=True
    )

    survey_config_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("survey_config.id", ondelete="CASCADE", onupdate="CASCADE")
    )

    text: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    survey: Mapped["UserSurveyConfig"] = relationship(back_populates="questions")
