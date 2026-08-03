from fastapi import APIRouter, Depends
from app.schemas.user import User
from app.models.user import User as UserModel
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=User)
async def get_current_user_profile(
    current_user: UserModel = Depends(get_current_user)
):
    """Get current user's profile."""
    return current_user
