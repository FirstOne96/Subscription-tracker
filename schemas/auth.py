from pydantic import BaseModel, EmailStr, Field
from schemas.user import UserPublic


class SignUpRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)

class SignInRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    token : str
    user : UserPublic