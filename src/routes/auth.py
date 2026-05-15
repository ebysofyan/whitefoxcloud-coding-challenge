from typing import Annotated

from fastapi import APIRouter, Body, HTTPException, status

from src.auth import authenticate
from src.models import LoginRequest, LoginResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(credentials: Annotated[LoginRequest, Body()]) -> LoginResponse:
    token = authenticate(credentials.username, credentials.password)
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    return LoginResponse(token=token)
