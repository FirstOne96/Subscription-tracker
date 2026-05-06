from fastapi import APIRouter, status
from controllers.auth import sign_up, sign_in, sign_out
from schemas.auth import SignUpRequest, SignInRequest, AuthResponse


router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post(
    "/sign-up",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
)
async def sign_up_route(body: SignUpRequest) -> AuthResponse:
    return await sign_up(body)


@router.post("/sign-in", response_model=AuthResponse)
async def sign_in_route(body: SignInRequest) -> AuthResponse:
    return await sign_in(body)


@router.post("/sign-out")
async def sign_out_route() -> dict:
    return await sign_out()