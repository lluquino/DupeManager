"""DupeManager — API: Episodes"""

from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def list_episodes():
    """Lista todos los grupos de episodios duplicados"""
    # TODO: Hito 1.6 — Implementar listado
    return []


@router.get("/{group_id}")
async def get_episode_group(group_id: str):
    """Obtiene un grupo específico de duplicados"""
    # TODO: Hito 1.6 — Implementar detalle
    return {"group_id": group_id, "copies": []}


@router.post("/{group_id}/action")
async def episode_action(group_id: str):
    """Ejecuta una acción sobre un grupo (keep/ignore/skip)"""
    # TODO: Hito 2.1 — Implementar acciones
    return {"status": "not_implemented"}
