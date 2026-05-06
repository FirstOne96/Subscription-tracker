from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from controllers.users import get_users, get_user
from middleware.auth import get_current_user
from models.user import User
from schemas.user import UserPublic


router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/", response_model=List[UserPublic])
async def get_users_route() -> List[UserPublic]:
    return await get_users()


@router.get(
    "/{user_id}",
    response_model=UserPublic,
)
async def get_user_route(
    user_id: str,
    current_user: User = Depends(get_current_user),
) -> UserPublic:
    return await get_user(user_id)


@router.post("/")
async def create_user_route() -> dict:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="User creation is handled via /api/v1/auth/sign-up",
    )


@router.put("/{user_id}")
async def update_user_route(user_id: str) -> dict:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="User update is not yet implemented",
    )


@router.delete("/{user_id}")
async def delete_user_route(user_id: str) -> dict:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="User deletion is not yet implemented",
    )