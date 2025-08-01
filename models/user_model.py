from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from models.base_model import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Enum as SqlEnum
from .enums import UserRole

class User(SQLAlchemyBaseUserTableUUID, Base):
    role:Mapped[UserRole] = mapped_column(
        SqlEnum(UserRole,
                name="role",
                native_enum=False),
        nullable=False,
        default="researcher"
    )