from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/healthcheck")
async def healthcheck():
    return {"router": "users", "status": "ok"}