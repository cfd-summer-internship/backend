from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from models.base_model import Base
from models.study_config_model import StudyConfiguration
from models.study_result_model import StudyResults


class Study(Base):
    """
    This is the main study entity.

    It contains a reference to the study configuration, as well as the study results.
    It contains columns for the researcher and a timestamp for its creation.
    """
    __tablename__ = "study"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True
    )

    # # STUDY CONFIG ID (FK, 1:1)
    # configuration_id: Mapped[uuid.UUID] = mapped_column(
    #     UUID(as_uuid=True),
    #     ForeignKey("study_config.id", ondelete="CASCADE", onupdate="CASCADE"),
    #     unique=True,
    # )

    researcher: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True)
    )

    # REFERENCE TO STUDY CONFIG ONE-TO-ONE
    # config: Mapped[StudyConfiguration] = relationship(back_populates="study")

    configurations: Mapped[list[StudyConfiguration]] = relationship()

    # REFERENCE TO STUDY RESULTS ONE-TO-MANY
    results: Mapped[list[StudyResults]] = relationship()