from fastapi import HTTPException, status
from passlib.context import CryptContext
from models.user import User
from schemas.auth import SignUpRequest, SignInRequest, AuthResponse
from schemas.user import UserPublic
from utils.jwt import create_access_token


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def sign_up(body: SignUpRequest) -> AuthResponse:
    # Check for existing user
    existing = await User.find_one(User.email == body.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists",
        )
    
    # Hash the password
    hashed_password = pwd_context.hash(body.password)
    
    # Create and insert the user
    user = User(
        name=body.name,
        email=body.email,
        password=hashed_password,
    )
    await user.insert()
    
    # Generate JWT token
    token = create_access_token(user_id=str(user.id))
    
    # Build the response
    return AuthResponse(
        token=token,
        user=UserPublic(
            id=str(user.id),
            name=user.name,
            email=user.email,
        ),
    )

async def sign_in(body: SignInRequest) -> AuthResponse:
    user = await User.find_one(User.email == body.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    if not pwd_context.verify(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    
    token = create_access_token(user_id=str(user.id))
    return AuthResponse(
        token=token,
        user=UserPublic(id=str(user.id), name=user.name, email=user.email),
    )

async def sign_out() -> dict:
    return {"success": True, "message": "Logged out successfully"}