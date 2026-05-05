from datetime import datetime, timezone
from beanie import Document, Insert, Replace, before_event
from pydantic import EmailStr, Field
from pymongo import IndexModel, ASCENDING


class User(Document):
    name : str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "users"
        indexes = [
            IndexModel([("email", ASCENDING)], unique=True)
        ]
    
    @before_event(Insert)
    async def set_created_at(self):
        self.created_at = datetime.now(timezone.utc)

    @before_event(Insert, Replace)
    async def set_updated_at(self):
        self.updated_at = datetime.now(timezone.utc)
