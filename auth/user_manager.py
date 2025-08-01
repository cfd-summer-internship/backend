import uuid
from typing import Optional

from fastapi import Depends, HTTPException, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin

from settings import get_settings
from models.user_model import User
from db.client import get_user_db
from auth.authentication_backend import auth_backend
from models.enums import UserRole

settings = get_settings()
SECRET = settings.auth


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        await self.user_db.update(user, {"role": UserRole.RESEARCHER})
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")

    async def promote_to_admin(self,user:User, request: Optional[Request] = None):
        return await self.user_db.update(user,{"role":UserRole.ADMIN})
    
    async def promote_to_staff(self,user:User, request: Optional[Request] = None):
        return await self.user_db.update(user,{"role":UserRole.STAFF})
    
    async def demote_user(self,user:User, request: Optional[Request] = None):
        return await self.user_db.update(user,{"role":UserRole.RESEARCHER})

# DI
async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)

current_superuser = fastapi_users.current_user(active=True, superuser=True)


def require_role(*allowed_roles: UserRole):
    def checker(user: User = Depends(current_active_user)):
        if user.role not in allowed_roles:
            raise HTTPException(403, "Forbidden")
        return user

    return checker
