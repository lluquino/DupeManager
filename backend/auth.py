"""DupeManager — Autenticación JWT + Jellyfin"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from backend.config import settings
from backend.jellyfin.client import jellyfin


# ── Modelos ───────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    token: str
    user: dict


class UserInfo(BaseModel):
    sub: str
    name: str
    exp: int


# ── Security ──────────────────────────────────────────────

security = HTTPBearer()


# ── Funciones ─────────────────────────────────────────────

def create_jwt(user_id: str, username: str, jellyfin_token: str) -> str:
    """Crea un JWT para el usuario"""
    payload = {
        "sub": user_id,
        "name": username,
        "jellyfin_token": jellyfin_token,
        "exp": datetime.now(timezone.utc) + timedelta(hours=settings.jwt_expiry_hours),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def decode_jwt(token: str) -> dict:
    """Decodifica y valida un JWT"""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )


async def login_with_jellyfin(username: str, password: str) -> TokenResponse:
    """Autentica contra Jellyfin y devuelve JWT"""
    try:
        result = await jellyfin.authenticate(username, password)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
        )

    access_token = result.get("AccessToken")
    user_id = result.get("User", {}).get("Id")

    if not access_token or not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Respuesta inválida de Jellyfin",
        )

    # Verificar si es admin
    user_info = await jellyfin.get_user(user_id, access_token)
    is_admin = user_info.get("Policy", {}).get("IsAdministrator", False)

    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden acceder a DupeManager",
        )

    # Crear JWT propio
    token = create_jwt(user_id, username, access_token)

    return TokenResponse(
        token=token,
        user={
            "id": user_id,
            "name": username,
            "isAdmin": True,
        },
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Dependency para obtener el usuario actual desde el JWT"""
    payload = decode_jwt(credentials.credentials)
    return {
        "sub": payload.get("sub"),
        "name": payload.get("name"),
        "jellyfin_token": payload.get("jellyfin_token"),
    }
