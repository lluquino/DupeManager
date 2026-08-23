"""DupeManager — API: Ignored"""

from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def list_ignored():
    """Lista todos los duplicados ignorados"""
    # TODO: Hito 1.6 — Implementar listado
    return []


@router.post("/{group_id}/restore")
async def restore_ignored(group_id: str):
    """Restaura un grupo ignorado a pendiente"""
    # TODO: Hito 1.6 — Implementar restaurar
    return {"status": "not_implemented"}


@router.post("/restore-many")
async def restore_many():
    """Restaura múltiples grupos ignorados"""
    # TODO: Hito 1.6 — Implementar restaurar múltiple
    return {"status": "not_implemented"}
