from fastapi import APIRouter, Depends
from auth.user_manager import current_active_user

from models.user_model import User

router = APIRouter(prefix="/user", tags=["user"])

@router.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}