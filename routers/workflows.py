from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/workflows", tags=["workflows"])


@router.get("/healthcheck")
async def healthcheck():
    return {"router": "workflows", "status": "ok"}