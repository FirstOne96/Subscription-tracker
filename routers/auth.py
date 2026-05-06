from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.get("/healthcheck")
async def healthcheck():
    return {"router": "auth", "status": "ok"}