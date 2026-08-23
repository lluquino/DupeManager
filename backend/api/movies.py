"""DupeManager — API: Movies"""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from backend.database import async_session, MovieDuplicate, MovieCopy, DuplicateStatus
from backend.auth import get_current_user
from backend.actions.manager import keep_best_and_remove_others, ignore_group

router = APIRouter()


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
        
        # Filtrar por estado
        if status:
            query = query.where(MovieDuplicate.status == status)
        
        # Ordenar por nombre
        query = query.order_by(MovieDuplicate.name)
        
        result = await session.execute(query)
        groups = result.scalars().all()
        
        # Aplicar búsqueda
        if search:
            search_lower = search.lower()
            groups = [
                g for g in groups
                if search_lower in (g.name or "").lower()
            ]
    
    return [
        {
            "groupId": g.group_id,
            "name": g.name,
            "year": g.year,
            "status": g.status,
            "totalSize": g.total_size,
            "copies": [
                {
                    "id": c.id,
                    "jellyfinItemId": c.jellyfin_item_id,
                    "path": c.path,
                    "filename": c.filename,
                    "size": c.size,
                    "resolution": c.resolution,
                    "codec": c.codec,
                    "qualityScore": c.quality_score,
                    "isBest": c.is_best,
                }
                for c in g.copies
            ],
        }
        for g in groups
    ]


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
    
    return {
        "groupId": group.group_id,
        "name": group.name,
        "year": group.year,
        "status": group.status,
        "totalSize": group.total_size,
        "copies": [
            {
                "id": c.id,
                "jellyfinItemId": c.jellyfin_item_id,
                "path": c.path,
                "filename": c.filename,
                "size": c.size,
                "resolution": c.resolution,
                "codec": c.codec,
                "qualityScore": c.quality_score,
                "isBest": c.is_best,
            }
            for c in group.copies
        ],
    }


@router.post("/{group_id}/action")
async def movie_action(
    group_id: str,
    body: dict,
    user: dict = Depends(get_current_user),
):
    """
    Ejecuta una acción sobre un grupo:
    - keep: Conservar la mejor, eliminar las peores
    - ignore: Marcar como ignorado
    - skip: No hacer nada
    """
    action = body.get("action")
    
    if action == "keep":
        from backend.config import settings
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
