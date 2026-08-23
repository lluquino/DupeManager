"""DupeManager — API: Dashboard"""

from fastapi import APIRouter
from sqlalchemy import select, func
from backend.database import async_session, EpisodeDuplicate, MovieDuplicate, ScanStatus

router = APIRouter()


@router.get("")
async def get_dashboard():
    """Obtiene estadísticas del dashboard"""
    async with async_session() as session:
        # Contar episodios duplicados (grupos pendientes)
        ep_result = await session.execute(
            select(func.count(EpisodeDuplicate.id)).where(
                EpisodeDuplicate.status == "pending"
            )
        )
        pending_episodes = ep_result.scalar() or 0

        # Contar películas duplicadas (grupos pendientes)
        movie_result = await session.execute(
            select(func.count(MovieDuplicate.id)).where(
                MovieDuplicate.status == "pending"
            )
        )
        pending_movies = movie_result.scalar() or 0

        # Total de grupos duplicados
        total_duplicates = pending_episodes + pending_movies

        # Calcular espacio recuperable
        ep_size_result = await session.execute(
            select(func.sum(EpisodeDuplicate.total_size)).where(
                EpisodeDuplicate.status == "pending"
            )
        )
        ep_size = ep_size_result.scalar() or 0

        movie_size_result = await session.execute(
            select(func.sum(MovieDuplicate.total_size)).where(
                MovieDuplicate.status == "pending"
            )
        )
        movie_size = movie_size_result.scalar() or 0

        recoverable_gb = round((ep_size + movie_size) / (1024**3), 2)

        # Último escaneo
        scan_result = await session.execute(select(ScanStatus).limit(1))
        scan_status = scan_result.scalar_one_or_none()

    return {
        "pendingEpisodes": pending_episodes,
        "pendingMovies": pending_movies,
        "totalDuplicates": total_duplicates,
        "recoverableSizeGB": recoverable_gb,
        "lastScan": scan_status.last_scan_at.isoformat() if scan_status and scan_status.last_scan_at else None,
    }
