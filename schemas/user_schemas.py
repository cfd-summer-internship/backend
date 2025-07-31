import uuid
from fastapi_users import schemas


class UserRead(schemas.BaseUser[uuid.UUID]):
    #Add properties as needed must match UserModel
    pass


class UserCreate(schemas.BaseUserCreate):
    #Add properties as needed must match UserModel
    pass


class UserUpdate(schemas.BaseUserUpdate):
    #Add properties as needed must match UserModel
    pass
