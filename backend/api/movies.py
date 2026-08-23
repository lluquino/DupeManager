"""DupeManager — API: Movies"""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from backend.database import async_session, MovieDuplicate, MovieCopy, DuplicateStatus
from backend.auth import get_current_user

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
    """Ejecuta una acción sobre un grupo (keep/ignore/skip)"""
    action = body.get("action")
    
    async with async_session() as session:
        query = select(MovieDuplicate).where(
            MovieDuplicate.group_id == group_id
        )
        result = await session.execute(query)
        group = result.scalar_one_or_none()
        
        if not group:
            return {"error": "Grupo no encontrado"}
        
        if action == "keep":
            group.status = DuplicateStatus.RESOLVED
        elif action == "ignore":
            group.status = DuplicateStatus.IGNORED
        elif action == "skip":
            pass
        else:
            return {"error": f"Acción no válida: {action}"}
        
        await session.commit()
    
    return {"success": True, "action": action, "groupId": group_id}
