from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


class SubscriptionCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    price: float = Field(..., ge=0)
    currency: Literal["USD", "EUR", "CZK", "UAH"] = "CZK"
    frequency: Literal["daily", "weekly", "monthly", "yearly"] = "monthly"
    category: Literal["entertainment", "utilities", "education", "health", "sport", "finance", "other"]
    payment_method: str
    start_date: datetime

class SubscriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    price: float
    currency: str
    frequency: str
    category: str
    payment_method: str
    status: str
    start_date: datetime
    renewal_date: datetime
    user_id: str
    created_at: datetime
    updated_at: datetime