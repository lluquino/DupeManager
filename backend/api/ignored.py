"""DupeManager — API: Ignored"""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from backend.database import async_session, EpisodeDuplicate, MovieDuplicate
from backend.auth import get_current_user
from backend.actions.manager import restore_group, restore_many_groups

router = APIRouter()


@router.get("")
async def list_ignored(user: dict = Depends(get_current_user)):
    """Lista todos los duplicados ignorados"""
    async with async_session() as session:
        # Buscar episodios ignorados
        ep_query = select(EpisodeDuplicate).where(
            EpisodeDuplicate.status == "ignored"
        )
        ep_result = await session.execute(ep_query)
        ep_groups = ep_result.scalars().all()
        
        # Buscar películas ignoradas
        movie_query = select(MovieDuplicate).where(
            MovieDuplicate.status == "ignored"
        )
        movie_result = await session.execute(movie_query)
        movie_groups = movie_result.scalars().all()
    
    ignored = []
    
    for g in ep_groups:
        ignored.append({
            "groupId": g.group_id,
            "name": f"{g.series_name} - S{g.season:02d}E{g.episode:02d}",
            "itemType": "episode",
            "ignoredAt": g.updated_at.isoformat() if g.updated_at else None,
        })
    
    for g in movie_groups:
        ignored.append({
            "groupId": g.group_id,
            "name": f"{g.name} ({g.year})" if g.year else g.name,
            "itemType": "movie",
            "ignoredAt": g.updated_at.isoformat() if g.updated_at else None,
        })
    
    return ignored


@router.post("/{group_id}/restore")
async def restore_ignored(group_id: str, user: dict = Depends(get_current_user)):
    """Restaura un grupo ignorado a pendiente"""
    result = await restore_group(group_id)
    return result


@router.post("/restore-many")
async def restore_many(body: dict = None, user: dict = Depends(get_current_user)):
    """Restaura múltiples grupos ignorados"""
    if not body or "groupIds" not in body:
        return {"success": False, "error": "groupIds requerido"}
    
    result = await restore_many_groups(body["groupIds"])
    return result
