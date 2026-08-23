"""DupeManager — Detector de Duplicados"""

import json
import hashlib
from pathlib import Path
from typing import Optional
from datetime import datetime, timezone

from backend.scanner.normalizer import (
    normalize_name,
    normalize_series_name,
    extract_episode_from_filename,
    extract_season_from_path,
    extract_series_name_from_path,
    extract_movie_name_from_filename,
    extract_year_from_filename,
)
from backend.scanner.quality import calculate_quality_score
from backend.scanner.filesystem import get_file_size, get_path_for_display
from backend.database import (
    async_session,
    EpisodeDuplicate,
    EpisodeCopy,
    MovieDuplicate,
    MovieDuplicate as MovieDuplicateModel,
    MovieCopy,
    ScanStatus,
    DuplicateStatus,
)

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession


def generate_group_id(*args) -> str:
    """Genera un ID único para un grupo de duplicados."""
    content = "|".join(str(a) for a in args)
    return hashlib.md5(content.encode()).hexdigest()[:12]


async def scan_episodes(
    session: AsyncSession,
    items: list[dict],
    media_path: str = "/media",
    progress_callback=None,
) -> dict:
    """
    Escanea episodios y detecta duplicados.
    
    Args:
        session: Sesión de BD
        items: Lista de items de Jellyfin
        media_path: Ruta base de medios
        progress_callback: Función para reportar progreso
    
    Returns:
        dict con estadísticas del escaneo
    """
    stats = {"total": len(items), "duplicates": 0, "groups": 0}
    
    # Agrupar por (serie_normalizada, temporada, episodio)
    groups: dict[str, list[dict]] = {}
    
    for i, item in enumerate(items):
        if progress_callback:
            progress_callback(i + 1, len(items), f"Procesando: {item.get('SeriesName', 'Episodio')}")
        
        path = item.get("Path", "")
        if not path:
            continue
        
        # Extraer información
        series_name = item.get("SeriesName", "")
        season = item.get("SeasonIndexNumber")
        episode = item.get("IndexNumber")
        
        # Si no hay episode number de Jellyfin, intentar extraer del filename
        if episode is None:
            episode = extract_episode_from_filename(path)
        
        # Si no hay season, intentar extraer de la ruta
        if season is None:
            season = extract_season_from_path(path)
        
        # Si aún no tenemos episode, saltar (evita falsos positivos)
        if episode is None:
            continue
        
        # Normalizar para agrupación
        norm_series = normalize_series_name(series_name)
        season = season or 0
        
        # Generar clave de agrupación
        key = f"{norm_series}|{season}|{episode}"
        
        if key not in groups:
            groups[key] = []
        
        groups[key].append({
            "item": item,
            "series_name": series_name,
            "season": season,
            "episode": episode,
            "norm_series": norm_series,
        })
    
    # Identificar duplicados (grupos con >1 item)
    duplicate_groups = {k: v for k, v in groups.items() if len(v) > 1}
    
    stats["groups"] = len(duplicate_groups)
    
    # Limpiar grupos existentes de episodios
    await session.execute(delete(EpisodeCopy))
    await session.execute(delete(EpisodeDuplicate))
    
    # Guardar duplicados en BD
    for key, items_list in duplicate_groups.items():
        parts = key.split("|")
        norm_series = parts[0]
        season = int(parts[1])
        episode = int(parts[2])
        series_name = items_list[0]["series_name"]
        
        group_id = generate_group_id(norm_series, season, episode)
        
        # Crear grupo
        group = EpisodeDuplicate(
            group_id=group_id,
            series_name=series_name,
            normalized_series=norm_series,
            season=season,
            episode=episode,
            status=DuplicateStatus.PENDING,
        )
        session.add(group)
        await session.flush()  # Para obtener el ID
        
        total_size = 0
        copies_data = []
        
        for item_data in items_list:
            item = item_data["item"]
            path = item.get("Path", "")
            filename = Path(path).name
            
            # Obtener tamaño del archivo
            size = get_file_size(path) or item.get("Size", 0) or 0
            total_size += size
            
            # Calcular quality score
            media_streams = None
            if item.get("MediaStreams"):
                media_streams = item["MediaStreams"]
            
            quality = calculate_quality_score(filename, size, media_streams)
            
            copy = EpisodeCopy(
                duplicate_id=group.id,
                jellyfin_item_id=item.get("Id"),
                path=path,
                filename=filename,
                size=size,
                resolution=quality["resolution"],
                codec=quality["codec"],
                quality_score=quality["score"],
                media_streams_json=json.dumps(media_streams) if media_streams else None,
            )
            session.add(copy)
            copies_data.append({"copy": copy, "score": quality["score"], "size": size})
        
        # Marcar la mejor copia
        if copies_data:
            best = max(copies_data, key=lambda x: (x["score"], x["size"]))
            best["copy"].is_best = True
        
        # Actualizar tamaño total del grupo
        group.total_size = total_size
        stats["duplicates"] += len(items_list)
    
    await session.commit()
    
    return stats


async def scan_movies(
    session: AsyncSession,
    items: list[dict],
    media_path: str = "/media",
    progress_callback=None,
) -> dict:
    """
    Escanea películas y detecta duplicados.
    
    Args:
        session: Sesión de BD
        items: Lista de items de Jellyfin
        media_path: Ruta base de medios
        progress_callback: Función para reportar progreso
    
    Returns:
        dict con estadísticas del escaneo
    """
    stats = {"total": len(items), "duplicates": 0, "groups": 0}
    
    # Agrupar por (nombre_normalizado, año)
    groups: dict[str, list[dict]] = {}
    
    for i, item in enumerate(items):
        if progress_callback:
            progress_callback(i + 1, len(items), f"Procesando: {item.get('Name', 'Película')}")
        
        path = item.get("Path", "")
        if not path:
            continue
        
        name = item.get("Name", "")
        year = item.get("ProductionYear")
        
        # Extraer nombre y año del filename si es necesario
        filename = Path(path).name
        if not name:
            name = extract_movie_name_from_filename(filename)
        if not year:
            year = extract_year_from_filename(filename)
        
        # Normalizar para agrupación
        norm_name = normalize_name(name)
        
        # Generar clave de agrupación
        key = f"{norm_name}|{year or 0}"
        
        if key not in groups:
            groups[key] = []
        
        groups[key].append({
            "item": item,
            "name": name,
            "year": year,
            "norm_name": norm_name,
        })
    
    # Identificar duplicados (grupos con >1 item)
    duplicate_groups = {k: v for k, v in groups.items() if len(v) > 1}
    
    stats["groups"] = len(duplicate_groups)
    
    # Limpiar grupos existentes de películas
    await session.execute(delete(MovieCopy))
    await session.execute(delete(MovieDuplicateModel))
    
    # Guardar duplicados en BD
    for key, items_list in duplicate_groups.items():
        parts = key.split("|")
        norm_name = parts[0]
        year = int(parts[1]) if parts[1] != "0" else None
        name = items_list[0]["name"]
        
        group_id = generate_group_id(norm_name, year or 0)
        
        # Crear grupo
        group = MovieDuplicateModel(
            group_id=group_id,
            name=name,
            normalized_name=norm_name,
            year=year,
            status=DuplicateStatus.PENDING,
        )
        session.add(group)
        await session.flush()
        
        total_size = 0
        copies_data = []
        
        for item_data in items_list:
            item = item_data["item"]
            path = item.get("Path", "")
            filename = Path(path).name
            
            # Obtener tamaño
            size = get_file_size(path) or item.get("Size", 0) or 0
            total_size += size
            
            # Calcular quality score
            media_streams = None
            if item.get("MediaStreams"):
                media_streams = item["MediaStreams"]
            
            quality = calculate_quality_score(filename, size, media_streams)
            
            copy = MovieCopy(
                duplicate_id=group.id,
                jellyfin_item_id=item.get("Id"),
                path=path,
                filename=filename,
                size=size,
                resolution=quality["resolution"],
                codec=quality["codec"],
                quality_score=quality["score"],
                media_streams_json=json.dumps(media_streams) if media_streams else None,
            )
            session.add(copy)
            copies_data.append({"copy": copy, "score": quality["score"], "size": size})
        
        # Marcar la mejor copia
        if copies_data:
            best = max(copies_data, key=lambda x: (x["score"], x["size"]))
            best["copy"].is_best = True
        
        # Actualizar tamaño total
        group.total_size = total_size
        stats["duplicates"] += len(items_list)
    
    await session.commit()
    
    return stats


async def run_full_scan(
    jellyfin_token: str,
    progress_callback=None,
) -> dict:
    """
    Ejecuta un escaneo completo de duplicados.
    
    1. Obtiene todos los episodios de Jellyfin
    2. Obtiene todas las películas de Jellyfin
    3. Detecta duplicados en ambos
    4. Guarda resultados en BD
    
    Returns:
        dict con estadísticas del escaneo completo
    """
    from backend.config import settings
    import httpx
    
    jellyfin_url = settings.jellyfin_url.rstrip("/")
    api_key = settings.jellyfin_api_key
    
    stats = {
        "episodes": {"total": 0, "duplicates": 0, "groups": 0},
        "movies": {"total": 0, "duplicates": 0, "groups": 0},
        "started_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None,
    }
    
    async with async_session() as session:
        # Actualizar estado de escaneo (obtener o crear)
        print("[SCAN] Starting full scan...", flush=True)
        result = await session.execute(select(ScanStatus).where(ScanStatus.id == 1))
        scan_status = result.scalar_one_or_none()
        if not scan_status:
            scan_status = ScanStatus(id=1)
            session.add(scan_status)
        
        scan_status.running = True
        scan_status.progress = 0
        scan_status.message = "Obteniendo episodios de Jellyfin..."
        scan_status.error = None
        await session.commit()
        
        # Obtener todos los episodios
        print("[SCAN] Fetching episodes from Jellyfin...", flush=True)
        all_episodes = []
        start_index = 0
        limit = 500
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            while True:
                try:
                    params = {
                        "api_key": api_key,
                        "Recursive": "true",
                        "IncludeItemTypes": "Episode",
                        "Fields": "Path,MediaStreams,Size,ProductionYear,SeriesName,SeasonIndexNumber,IndexNumber,LocationType",
                        "Limit": limit,
                        "StartIndex": start_index,
                    }
                    response = await client.get(f"{jellyfin_url}/Items", params=params)
                    response.raise_for_status()
                    result = response.json()
                    
                    items = result.get("Items", [])
                    total = result.get("TotalRecordCount", 0)
                    all_episodes.extend(items)
                    start_index += len(items)
                    print(f"[SCAN] Episodes: {start_index}/{total}", flush=True)
                    
                    if start_index >= total:
                        break
                except Exception as e:
                    print(f"[SCAN] Error fetching episodes: {e}", flush=True)
                    break
        
        print(f"[SCAN] Total episodes fetched: {len(all_episodes)}", flush=True)
        stats["episodes"]["total"] = len(all_episodes)
        
        # Escanear episodios
        def ep_progress(current, total, message):
            progress = (current / total * 50) if total > 0 else 0
            if progress_callback:
                progress_callback(progress, message)
        
        ep_stats = await scan_episodes(session, all_episodes, progress_callback=ep_progress)
        stats["episodes"] = ep_stats
        
        # Actualizar progreso
        scan_status.progress = 50
        scan_status.message = "Obteniendo películas de Jellyfin..."
        await session.commit()
        
        # Obtener todas las películas
        print("[SCAN] Fetching movies from Jellyfin...", flush=True)
        all_movies = []
        start_index = 0
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            while True:
                try:
                    params = {
                        "api_key": api_key,
                        "Recursive": "true",
                        "IncludeItemTypes": "Movie",
                        "Fields": "Path,MediaStreams,Size,ProductionYear,LocationType",
                        "Limit": limit,
                        "StartIndex": start_index,
                    }
                    response = await client.get(f"{jellyfin_url}/Items", params=params)
                    response.raise_for_status()
                    result = response.json()
                    
                    items = result.get("Items", [])
                    total = result.get("TotalRecordCount", 0)
                    all_movies.extend(items)
                    start_index += len(items)
                    print(f"[SCAN] Movies: {start_index}/{total}", flush=True)
                    
                    if start_index >= total:
                        break
                except Exception as e:
                    print(f"[SCAN] Error fetching movies: {e}", flush=True)
                    break
        
        print(f"[SCAN] Total movies fetched: {len(all_movies)}", flush=True)
        stats["movies"]["total"] = len(all_movies)
        
        # Escanear películas
        def movie_progress(current, total, message):
            progress = 50 + (current / total * 50) if total > 0 else 50
            if progress_callback:
                progress_callback(progress, message)
        
        movie_stats = await scan_movies(session, all_movies, progress_callback=movie_progress)
        stats["movies"] = movie_stats
        
        # Finalizar escaneo
        scan_status.running = False
        scan_status.progress = 100
        scan_status.last_scan_at = datetime.now(timezone.utc)
        scan_status.message = "Escaneo completado"
        stats["completed_at"] = datetime.now(timezone.utc).isoformat()
        
        await session.commit()
    
    return stats
