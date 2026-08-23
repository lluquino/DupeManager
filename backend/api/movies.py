"""DupeManager — API: Movies"""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from backend.database import async_session, MovieDuplicate, MovieCopy, DuplicateStatus
from backend.auth import get_current_user
from backend.actions.manager import keep_best_and_remove_others, keep_selected_and_remove_others, ignore_group
from backend.api.helpers import format_copy

router = APIRouter()


def format_movie_group(g):
    """Formatea un grupo de películas con metadatos en cada copia"""
    copies = []
    for c in g.copies:
        copy_data = format_copy(c)
        copy_data["movieName"] = g.name
        copy_data["movieYear"] = g.year
        copies.append(copy_data)
    
    return {
        "groupId": g.group_id,
        "name": g.name,
        "year": g.year,
        "status": g.status,
        "totalSize": g.total_size,
        "copies": copies,
    }


@router.get("")
async def list_movies(
    status: str = None,
    search: str = None,
    user: dict = Depends(get_current_user),
):
    """Lista todos los grupos de películas duplicadas"""
    async with async_session() as session:
        query = select(MovieDuplicate).options(
            selectinload(MovieDuplicate.copies)
        )
        
        if status:
            query = query.where(MovieDuplicate.status == status)
        
        query = query.order_by(MovieDuplicate.name)
        
        result = await session.execute(query)
        groups = result.scalars().all()
        
        if search:
            search_lower = search.lower()
            groups = [
                g for g in groups
                if search_lower in (g.name or "").lower()
            ]
    
    return [format_movie_group(g) for g in groups]


@router.get("/{group_id}")
async def get_movie_group(group_id: str, user: dict = Depends(get_current_user)):
    """Obtiene un grupo específico de duplicados"""
    async with async_session() as session:
        query = select(MovieDuplicate).options(
            selectinload(MovieDuplicate.copies)
        ).where(MovieDuplicate.group_id == group_id)
        
        result = await session.execute(query)
        group = result.scalar_one_or_none()
        
        if not group:
            return {"error": "Grupo no encontrado"}
    
    return format_movie_group(group)


@router.post("/{group_id}/action")
async def movie_action(
    group_id: str,
    body: dict,
    user: dict = Depends(get_current_user),
):
    """
    Ejecuta una acción sobre un grupo:
    - keep: Conservar la(s) mejor(es), eliminar las peores
    - ignore: Marcar como ignorado
    - skip: No hacer nada
    """
    action = body.get("action")
    keep_copy_ids = body.get("keepCopyIds")
    
    if action == "keep":
        from backend.config import settings
        
        if keep_copy_ids:
            result = await keep_selected_and_remove_others(
                group_id,
                keep_copy_ids=keep_copy_ids,
                group_type="movie",
                trash_enabled=settings.trash_enabled,
            )
        else:
            result = await keep_best_and_remove_others(
                group_id,
                group_type="movie",
                trash_enabled=settings.trash_enabled,
            )
        return result
    
    elif action == "ignore":
        result = await ignore_group(group_id, group_type="movie")
        return result
    
    elif action == "skip":
        return {"success": True, "action": "skip", "groupId": group_id}
    
    else:
        return {"success": False, "error": f"Acción no válida: {action}"}
