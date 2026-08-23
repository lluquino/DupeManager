"""DupeManager — API: Dashboard"""

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from backend.database import async_session, EpisodeDuplicate, MovieDuplicate, ScanStatus
from backend.auth import get_current_user

router = APIRouter()


@router.get("")
async def get_dashboard(user: dict = Depends(get_current_user)):
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

        # Calcular espacio recuperable (sumar todas las copias excepto la mejor)
        # Simplificado: sumar total_size de todos los grupos pendientes
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

        # El espacio recuperable es aproximadamente la mitad del total
        # (asumiendo que mantenemos la mejor copia)
        recoverable_bytes = (ep_size + movie_size) / 2
        recoverable_gb = round(recoverable_bytes / (1024**3), 2)

        # Último escaneo
        scan_result = await session.execute(select(ScanStatus).limit(1))
        scan_status = scan_result.scalar_one_or_none()
        
        # Top 5 series con más duplicados
        top_series_query = select(
            EpisodeDuplicate.series_name,
            func.count(EpisodeDuplicate.id).label("count"),
        ).where(
            EpisodeDuplicate.status == "pending"
        ).group_by(
            EpisodeDuplicate.series_name
        ).order_by(
            func.count(EpisodeDuplicate.id).desc()
        ).limit(5)
        
        top_result = await session.execute(top_series_query)
        top_series = [
            {"name": row[0], "count": row[1]}
            for row in top_result.all()
        ]

    return {
        "pendingEpisodes": pending_episodes,
        "pendingMovies": pending_movies,
        "totalDuplicates": total_duplicates,
        "recoverableSizeGB": recoverable_gb,
        "lastScan": scan_status.last_scan_at.isoformat() if scan_status and scan_status.last_scan_at else None,
        "topSeries": top_series,
    }
