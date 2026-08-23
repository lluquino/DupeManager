"""DupeManager — API: Auth"""

from fastapi import APIRouter, HTTPException
from backend.auth import LoginRequest, login_with_jellyfin

router = APIRouter()


@router.post("/login")
async def login(request: LoginRequest):
    """Login contra Jellyfin (solo admins)"""
    return await login_with_jellyfin(request.username, request.password)
