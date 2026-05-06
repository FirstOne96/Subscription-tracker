from fastapi import APIRouter
from controllers.workflows import send_reminders, ReminderRequest


router = APIRouter(prefix="/api/v1/workflows", tags=["workflows"])


@router.post("/subscription/reminder")
async def send_reminders_route(body: ReminderRequest) -> dict:
    return await send_reminders(body)