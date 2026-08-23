"""DupeManager — API: Scan"""

from fastapi import APIRouter, Depends
from backend.auth import get_current_user
from backend.queue import scan_queue

router = APIRouter()


@router.post("")
async def start_scan(user: dict = Depends(get_current_user)):
    """
    Inicia un escaneo completo en background.
    
    Requiere autenticación de administrador.
    """
    jellyfin_token = user.get("jellyfin_token")
    if not jellyfin_token:
        return {"status": "error", "message": "Token de Jellyfin no disponible"}
    
    result = await scan_queue.start(jellyfin_token)
    return result


@router.get("/status")
async def scan_status():
    """Obtiene el estado del escaneo actual (no requiere auth)"""
    return scan_queue.get_status()
