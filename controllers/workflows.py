from beanie import PydanticObjectId
from bson.errors import InvalidId
from fastapi import HTTPException, status
from pydantic import BaseModel

from models.subscription import Subscription
from tasks.reminder import schedule_reminders


class ReminderRequest(BaseModel):
    subscription_id: str


async def send_reminders(body: ReminderRequest) -> dict:
    try:
        oid = PydanticObjectId(body.subscription_id)
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid subscription ID",
        )
    
    sub = await Subscription.get(oid)
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found",
        )
    
    task = schedule_reminders.delay(body.subscription_id)
    
    return {
        "success": True,
        "task_id": task.id,
        "subscription_id": body.subscription_id,
    }