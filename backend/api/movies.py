"""DupeManager — API: Movies"""

from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def list_movies():
    """Lista todos los grupos de películas duplicadas"""
    # TODO: Hito 1.6 — Implementar listado
    return []


@router.get("/{group_id}")
async def get_movie_group(group_id: str):
    """Obtiene un grupo específico de duplicados"""
    # TODO: Hito 1.6 — Implementar detalle
    return {"group_id": group_id, "copies": []}


@router.post("/{group_id}/action")
async def movie_action(group_id: str):
    """Ejecuta una acción sobre un grupo (keep/ignore/skip)"""
    # TODO: Hito 2.1 — Implementar acciones
    return {"status": "not_implemented"}
