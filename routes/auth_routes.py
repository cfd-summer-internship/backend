from fastapi import APIRouter
from auth.user_manager import fastapi_users
from auth.authentication_backend import auth_backend

from schemas.user_schemas import UserCreate, UserRead, UserUpdate



auth_router = APIRouter(prefix="/auth", tags=["auth"])

# LOGIN/LOGOUT
auth_router.include_router(fastapi_users.get_auth_router(auth_backend),prefix="/jwt")

# REGISTER
auth_router.include_router(fastapi_users.get_register_router(UserRead, UserCreate))

# USERS
auth_router.include_router(fastapi_users.get_users_router(UserRead, UserUpdate))


# TODO: ADD VERIFY ROUTE
