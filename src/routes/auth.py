from typing import Annotated

from fastapi import APIRouter, Body

from src.auth.token_store import authenticate
from src.core.exceptions import NotAuthenticatedError
from src.schemas import LoginRequest, LoginResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Authenticate and get a token",
)
def login(credentials: Annotated[LoginRequest, Body()]) -> LoginResponse:
    token = authenticate(credentials.username, credentials.password)
    if token is None:
        raise NotAuthenticatedError("Invalid username or password")
    return LoginResponse(token=token)
