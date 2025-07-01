import models.all_models
from models.base_model import Base
from sqlalchemy.orm import registry

print("Models registered in ORM:")
print(list(Base.registry._class_registry.keys()))
print("Tables in metadata:")
print(Base.metadata.tables.keys())
