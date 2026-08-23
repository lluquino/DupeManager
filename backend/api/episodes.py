"""DupeManager — API: Episodes"""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from backend.database import async_session, EpisodeDuplicate, EpisodeCopy, DuplicateStatus
from backend.auth import get_current_user
from backend.actions.manager import keep_best_and_remove_others, keep_selected_and_remove_others, ignore_group
from backend.api.helpers import format_copy

router = APIRouter()


def format_episode_group(g):
    """Formatea un grupo de episodios con metadatos en cada copia"""
    copies = []
    for c in g.copies:
        copy_data = format_copy(c)
        copy_data["seriesName"] = g.series_name
        copy_data["seasonNumber"] = g.season
        copy_data["episodeNumber"] = g.episode
        copies.append(copy_data)
    
    return {
        "groupId": g.group_id,
        "seriesName": g.series_name,
        "season": g.season,
        "episode": g.episode,
        "status": g.status,
        "totalSize": g.total_size,
        "copies": copies,
    }


@router.get("")
async def list_episodes(
    status: str = None,
    search: str = None,
    user: dict = Depends(get_current_user),
):
    """Lista todos los grupos de episodios duplicados"""
    async with async_session() as session:
        query = select(EpisodeDuplicate).options(
            selectinload(EpisodeDuplicate.copies)
        )
        
        if status:
            query = query.where(EpisodeDuplicate.status == status)
        
        query = query.order_by(
            EpisodeDuplicate.normalized_series,
            EpisodeDuplicate.season,
            EpisodeDuplicate.episode,
        )
        
        result = await session.execute(query)
        groups = result.scalars().all()
        
        if search:
            search_lower = search.lower()
            groups = [
                g for g in groups
                if search_lower in (g.series_name or "").lower()
                or search_lower in f"s{g.season:02d}e{g.episode:02d}"
            ]
    
    return [format_episode_group(g) for g in groups]


@router.get("/{group_id}")
async def get_episode_group(group_id: str, user: dict = Depends(get_current_user)):
    """Obtiene un grupo específico de duplicados"""
    async with async_session() as session:
        query = select(EpisodeDuplicate).options(
            selectinload(EpisodeDuplicate.copies)
        ).where(EpisodeDuplicate.group_id == group_id)
        
        result = await session.execute(query)
        group = result.scalar_one_or_none()
        
        if not group:
            return {"error": "Grupo no encontrado"}
    
    return format_episode_group(group)


@router.post("/{group_id}/action")
async def episode_action(
    group_id: str,
    body: dict,
    user: dict = Depends(get_current_user),
):
    """
    Ejecuta una acción sobre un grupo:
    - keep: Conservar la(s) mejor(es), eliminar las peores
      - keepCopyIds: [1, 3] → conserva estas copias específicas
      - Sin keepCopyIds → conserva la de mayor score
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
                group_type="episode",
                trash_enabled=settings.trash_enabled,
            )
        else:
            result = await keep_best_and_remove_others(
                group_id,
                group_type="episode",
                trash_enabled=settings.trash_enabled,
            )
        return result
    
    elif action == "ignore":
        result = await ignore_group(group_id, group_type="episode")
        return result
    
    elif action == "skip":
        return {"success": True, "action": "skip", "groupId": group_id}
    
    else:
        return {"success": False, "error": f"Acción no válida: {action}"}
