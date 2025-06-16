from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, relationship, Mapped,mapped_column
from sqlalchemy import Enum as SqlEnum
from enum import Enum
import uuid

Base = declarative_base()

class DisplayMethodEnum(str,Enum):
    SEQUENTIAL = "sequential"
    RANDOM = "random"

class ResponseMethodEnum(str,Enum):
    BINARY = "binary"
    GRADIENT = "gradient"

class StudyConfiguration(Base):
    __tablename__ = "study_config"

    #SET UUID FOR ID and PK
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True
    )

    #SHOW USER RESULTS
    show_results:Mapped[Boolean]= mapped_column(
        Boolean,
        nullable=False
    )

    #FK TO USER ID
    # researcher_id:Mapped[String]=mapped_column(
    #     String,
    #     ForeignKey(
    #         "researcher.id",
    #         ondelete="CASCADE",
    #         onupdate="CASCADE",
    #     ),
    #     nullable=False
    # )

    #REFERENCE TO LEARNING CONFIG
    learning:Mapped["LearningConfiguration"]=relationship(
        back_populates="study",
        cascade="all, delete-orphan",
        uselist=False
    )

    #REFERENCE TO LEARNING CONFIG
    wait:Mapped["WaitingConfiguration"]=relationship(
        back_populates="study",
        cascade="all, delete-orphan",
        uselist=False
    )

    #REFERENCE TO LEARNING CONFIG
    experiment:Mapped["ExperimentConfiguration"]=relationship(
        back_populates="study",
        cascade="all, delete-orphan",
        uselist=False
    )

    #REFERENCE TO LEARNING CONFIG
    files:Mapped["UploadedFiles"]=relationship(
        back_populates="study",
        cascade="all, delete-orphan",
        uselist=False
    )

    #REFERENCE TO LEARNING CONFIG
    survey:Mapped["DemographicSurvey"]=relationship(
        back_populates="study",
        cascade="all, delete-orphan",
        uselist=False
    )

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

    consent_form:Mapped[String] = mapped_column(
        String,
        nullable=False
    )

    image_list:Mapped[String] = mapped_column(
        String,
        nullable=False
    )

    instruction_set:Mapped[String] = mapped_column(
        String,
        nullable=False
    )

    debrief:Mapped[String] = mapped_column(
        String,
        nullable=False
    )

    #REFERENCE TO STUDY CONFIG
    study : Mapped[StudyConfiguration]=relationship(back_populates="files")

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
    display_duration:Mapped[Integer]= mapped_column(
        Integer,
        nullable=False
    )

    #PAUSE DURATION
    pause_duration:Mapped[Integer] = mapped_column(
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
    display_duration:Mapped[Integer]= mapped_column(
        Integer,
        nullable=False
    )

    #REFERENCE TO STUDY CONFIG
    study : Mapped[StudyConfiguration]=relationship(back_populates="wait")

#EXPIREMENT PHASE CONFIG
class ExperimentConfiguration(Base):
    __tablename__ ="experiment_config"

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
    display_duration:Mapped[Integer]= mapped_column(
        Integer,
        nullable=False
    )

    #PAUSE DURATION
    pause_duration:Mapped[Integer] = mapped_column(
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

    #RESPONSE METHOD
    #Takes either BINARY or GRADIENT
    response_method:Mapped[ResponseMethodEnum] = mapped_column(
        SqlEnum(ResponseMethodEnum,
                name="response_method",
                native_enum=False),
        nullable=False
    )

    #REFERENCE TO STUDY CONFIG
    study : Mapped[StudyConfiguration]=relationship(back_populates="experiment")

class DemographicSurvey(Base):
    __tablename__ ="survey_config"

    #SET UUID FOR ID
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
    
    #BI-DIRECTIONAL REFERENCE TO STUDY CONFIG
    study: Mapped[StudyConfiguration]=relationship(back_populates="survey")

    #BI-DIRECTIONAL REFERENCE TO SUVERY QUESTIONS
    questions:Mapped[list["SurveyQuestion"]]=relationship(back_populates="survey")

    #BI-DIRECTIONAL REFERENCE TO SUVERY QUESTIONS
    answers:Mapped[list["SurveyAnswer"]]=relationship(back_populates="survey")

class SurveyQuestion (Base):
    __tablename__ ="survey_question"

    id:Mapped[Integer]=mapped_column(
        Integer,
        nullable=False,
        primary_key=True,
        autoincrement=True
    )

    #SURVEY ID (PK,FK)
    survey_config_id:Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "survey_config.id", 
            ondelete="CASCADE", 
            onupdate="CASCADE"),
        unique=True
    )

    text:Mapped[String] = mapped_column(
        String,
        nullable=False
    )

    #REFERENCE TO STUDY CONFIG
    survey : Mapped[DemographicSurvey]=relationship(back_populates="questions")

class SurveyAnswer (Base):
    __tablename__ ="survey_answer"

    id:Mapped[Integer]=mapped_column(
        Integer,
        nullable=False,
        primary_key=True,
        autoincrement=True
    )

    #SURVEY ID (PK,FK)
    survey_config_id:Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "survey_config.id", 
            ondelete="CASCADE", 
            onupdate="CASCADE"),
            unique=True
    )

    text:Mapped[String] = mapped_column(
        String,
        nullable=False
    )

    #REFERENCE TO STUDY CONFIG
    survey : Mapped[DemographicSurvey]=relationship(back_populates="answers")