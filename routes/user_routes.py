import uuid
from fastapi import APIRouter, Depends
from auth.user_manager import UserManager, current_active_user, current_superuser, get_user_manager, require_role

from models.enums import UserRole
from models.user_model import User

router = APIRouter(prefix="/user", tags=["user"])

@router.get("/authenticated_route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}

@router.get("/staff_route")
async def staff_route(user: User = Depends(require_role(UserRole.ADMIN,UserRole.STAFF))):
    return {"message": f"Hello staff {user.email}!"}

@router.get("/admin_route")
async def admin_route(user: User = Depends(require_role(UserRole.ADMIN))):
    return {"message": f"Hello admin {user.email}!"}

@router.get("/elevate_admin")
async def elevate_to_admin(
    user_id:uuid.UUID,
    user_manager:UserManager = Depends(get_user_manager),
    superuser:User = Depends(current_superuser),
    ):
    if superuser:
        user = await user_manager.get(user_id)
        return await user_manager.promote_to_admin(user)
    
@router.get("/elevate_staff")
async def elevate_to_staff(
    user_id:uuid.UUID,
    user_manager:UserManager = Depends(get_user_manager),
    superuser:User = Depends(current_superuser),
    ):
    if superuser:
        user = await user_manager.get(user_id)
        return await user_manager.promote_to_staff(user)
    
@router.get("/demote_user")
async def demote_user(
    user_id:uuid.UUID,
    user_manager:UserManager = Depends(get_user_manager),
    superuser:User = Depends(current_superuser),
    ):
    if superuser:
        user = await user_manager.get(user_id)
        return await user_manager.demote_user(user)
