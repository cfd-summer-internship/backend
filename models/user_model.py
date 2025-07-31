from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from models.base_model import Base

class User(SQLAlchemyBaseUserTableUUID, Base):
    pass