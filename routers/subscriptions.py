from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/subscriptions", tags=["subscriptions"])


@router.get("/healthcheck")
async def healthcheck():
    return {"router": "subscriptions", "status": "ok"}