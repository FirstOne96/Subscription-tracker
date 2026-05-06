from typing import List
from beanie import PydanticObjectId
from bson.errors import InvalidId
from fastapi import HTTPException, status
from models.user import User
from schemas.user import UserPublic


async def get_users() -> List[UserPublic]:
    users = await User.find_all().to_list()
    return [UserPublic(id=str(user.id), name=user.name, email=user.email) for user in users]


async def get_user(user_id: str) -> UserPublic:
    try:
        oid = PydanticObjectId(user_id)
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format",
        )
    
    user = await User.get(oid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return UserPublic(id=str(user.id), name=user.name, email=user.email)