from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email: EmailStr
