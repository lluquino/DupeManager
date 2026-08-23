"""DupeManager — API: Scan"""

from fastapi import APIRouter

router = APIRouter()


@router.post("")
async def start_scan():
    """Inicia un escaneo completo en background"""
    # TODO: Hito 1.2 — Implementar escaneo
    return {"status": "not_implemented", "message": "Scanner no implementado aún"}


@router.get("/status")
async def scan_status():
    """Obtiene el estado del escaneo actual"""
    # TODO: Hito 1.2 — Implementar estado
    return {"running": False, "progress": 0, "message": "Idle"}
