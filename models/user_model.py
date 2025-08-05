from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from models.base_model import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ARRAY, Enum as SqlEnum
from .enums import UserRole

class User(SQLAlchemyBaseUserTableUUID, Base):
    role:Mapped[list[UserRole]] = mapped_column(
        ARRAY(SqlEnum(UserRole,
                name="role",
                native_enum=False)),
        nullable=False,
        default=[UserRole.RESEARCHER]
    )