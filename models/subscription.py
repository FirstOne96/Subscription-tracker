from datetime import datetime, timedelta, timezone
from typing import Literal, Optional
from beanie import Document, Link, Insert, Replace, SaveChanges, before_event
from pydantic import Field, field_validator
from pymongo import IndexModel, ASCENDING
from models.user import User


class Subscription(Document):
    name : str = Field(..., min_length=2, max_length=50)
    price : float = Field(..., ge=0)
    currency : Literal["USD", "EUR", "CZK", "UAH"] = "CZK"
    frequency : Literal["daily", "weekly", "monthly", "yearly"] = "monthly"
    category : Literal["entertainment", "utilities", "education", "health", "sport", "finance", "other"]
    payment_method : str 
    status : Literal["active", "cancelled", "expired"] = "active"
    start_date : datetime
    renewal_date : Optional[datetime] = None
    user : Link[User]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "subscriptions"
        indexes = [
            IndexModel([("user", ASCENDING)])
        ]

    @field_validator("start_date")
    @classmethod
    def validate_start_date_in_past(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        if value > datetime.now(timezone.utc):
            raise ValueError("Start date cannot be in the future")
        return value
    
    @before_event(Insert, Replace, SaveChanges)
    async def compute_renewal_and_status(self):
        days = {"daily": 1, "weekly": 7, "monthly": 30, "yearly": 365}[self.frequency]
        if self.renewal_date is None:
            self.renewal_date = self.start_date + timedelta(days=days)

        if self.status != "cancelled" and self.renewal_date < datetime.now(timezone.utc):
            self.status = "expired"
            