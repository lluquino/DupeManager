"""DupeManager — Gestión de Acciones sobre Archivos"""

import os
from pathlib import Path
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import (
    async_session,
    EpisodeDuplicate,
    EpisodeCopy,
    MovieDuplicate,
    MovieCopy,
    DuplicateStatus,
)
from backend.scanner.filesystem import move_to_trash, delete_file, get_trash_path
from backend.config import settings


async def keep_best_and_remove_others(
    group_id: str,
    group_type: str = "episode",
    trash_enabled: bool = True,
) -> dict:
    """
    Conserva la mejor copia y elimina las demás.
    
    Args:
        group_id: ID del grupo de duplicados
        group_type: "episode" o "movie"
        trash_enabled: Si True, mover a papelera. Si False, eliminar directamente.
    
    Returns:
        dict con resultado de la operación
    """
    async with async_session() as session:
        # Obtener el grupo con sus copias
        if group_type == "episode":
            query = select(EpisodeDuplicate).where(
                EpisodeDuplicate.group_id == group_id
            )
            result = await session.execute(query)
            group = result.scalar_one_or_none()
            
            if not group:
                return {"success": False, "error": "Grupo no encontrado"}
            
            # Obtener copias ordenadas por score (mayor primero)
            copies_query = select(EpisodeCopy).where(
                EpisodeCopy.duplicate_id == group.id
            )
            copies_result = await session.execute(copies_query)
            copies = copies_result.scalars().all()
            
        elif group_type == "movie":
            query = select(MovieDuplicate).where(
                MovieDuplicate.group_id == group_id
            )
            result = await session.execute(query)
            group = result.scalar_one_or_none()
            
            if not group:
                return {"success": False, "error": "Grupo no encontrado"}
            
            copies_query = select(MovieCopy).where(
                MovieCopy.duplicate_id == group.id
            )
            copies_result = await session.execute(copies_query)
            copies = copies_result.scalars().all()
        else:
            return {"success": False, "error": f"Tipo no válido: {group_type}"}
        
        if not copies:
            return {"success": False, "error": "No hay copias en el grupo"}
        
        # Ordenar por score (mayor primero), luego por tamaño (mayor primero)
        sorted_copies = sorted(copies, key=lambda c: (c.quality_score, c.size), reverse=True)
        
        best_copy = sorted_copies[0]
        copies_to_remove = sorted_copies[1:]
        
        removed = []
        errors = []
        
        for copy in copies_to_remove:
            filepath = copy.path
            
            if not filepath or not os.path.exists(filepath):
                errors.append(f"Archivo no encontrado: {filepath}")
                continue
            
            try:
                if trash_enabled:
                    # Mover a papelera
                    trash_path = get_trash_path(filepath, settings.trash_path)
                    success = move_to_trash(filepath, settings.trash_path)
                else:
                    # Eliminar directamente
                    success = delete_file(filepath)
                
                if success:
                    removed.append(filepath)
                    # Eliminar de la BD
                    await session.delete(copy)
                else:
                    errors.append(f"Error al procesar: {filepath}")
            except Exception as e:
                errors.append(f"Error: {filepath} - {str(e)}")
        
        # Marcar grupo como resuelto
        group.status = DuplicateStatus.RESOLVED
        
        await session.commit()
    
    return {
        "success": True,
        "kept": best_copy.path,
        "removed": removed,
        "errors": errors,
        "removedCount": len(removed),
    }


async def ignore_group(group_id: str, group_type: str = "episode") -> dict:
    """
    Marca un grupo como ignorado.
    """
    async with async_session() as session:
        if group_type == "episode":
            query = select(EpisodeDuplicate).where(
                EpisodeDuplicate.group_id == group_id
            )
            result = await session.execute(query)
            group = result.scalar_one_or_none()
        elif group_type == "movie":
            query = select(MovieDuplicate).where(
                MovieDuplicate.group_id == group_id
            )
            result = await session.execute(query)
            group = result.scalar_one_or_none()
        else:
            return {"success": False, "error": f"Tipo no válido: {group_type}"}
        
        if not group:
            return {"success": False, "error": "Grupo no encontrado"}
        
        group.status = DuplicateStatus.IGNORED
        await session.commit()
    
    return {"success": True, "groupId": group_id, "status": "ignored"}


async def restore_group(group_id: str) -> dict:
    """
    Restaura un grupo ignorado a pendiente.
    """
    async with async_session() as session:
        # Buscar en episodios
        ep_query = select(EpisodeDuplicate).where(
            EpisodeDuplicate.group_id == group_id
        )
        result = await session.execute(ep_query)
        group = result.scalar_one_or_none()
        
        if group:
            group.status = DuplicateStatus.PENDING
            await session.commit()
            return {"success": True, "groupId": group_id, "status": "pending"}
        
        # Buscar en películas
        movie_query = select(MovieDuplicate).where(
            MovieDuplicate.group_id == group_id
        )
        result = await session.execute(movie_query)
        group = result.scalar_one_or_none()
        
        if group:
            group.status = DuplicateStatus.PENDING
            await session.commit()
            return {"success": True, "groupId": group_id, "status": "pending"}
        
        return {"success": False, "error": "Grupo no encontrado"}


async def restore_many_groups(group_ids: list[str]) -> dict:
    """
    Restaura múltiples grupos ignorados.
    """
    restored = 0
    
    for group_id in group_ids:
        result = await restore_group(group_id)
        if result.get("success"):
            restored += 1
    
    return {"success": True, "restored": restored}


async def keep_selected_and_remove_others(
    group_id: str,
    keep_copy_ids: list[int],
    group_type: str = "episode",
    trash_enabled: bool = True,
) -> dict:
    """
    Conserva las copias seleccionadas y elimina las demás.
    
    Args:
        group_id: ID del grupo de duplicados
        keep_copy_ids: Lista de IDs de copias a conservar
        group_type: "episode" o "movie"
        trash_enabled: Si True, mover a papelera. Si False, eliminar directamente.
    
    Returns:
        dict con resultado de la operación
    """
    async with async_session() as session:
        # Obtener el grupo con sus copias
        if group_type == "episode":
            query = select(EpisodeDuplicate).where(
                EpisodeDuplicate.group_id == group_id
            )
            result = await session.execute(query)
            group = result.scalar_one_or_none()
            
            if not group:
                return {"success": False, "error": "Grupo no encontrado"}
            
            copies_query = select(EpisodeCopy).where(
                EpisodeCopy.duplicate_id == group.id
            )
            copies_result = await session.execute(copies_query)
            copies = copies_result.scalars().all()
            
        elif group_type == "movie":
            query = select(MovieDuplicate).where(
                MovieDuplicate.group_id == group_id
            )
            result = await session.execute(query)
            group = result.scalar_one_or_none()
            
            if not group:
                return {"success": False, "error": "Grupo no encontrado"}
            
            copies_query = select(MovieCopy).where(
                MovieCopy.duplicate_id == group.id
            )
            copies_result = await session.execute(copies_query)
            copies = copies_result.scalars().all()
        else:
            return {"success": False, "error": f"Tipo no válido: {group_type}"}
        
        if not copies:
            return {"success": False, "error": "No hay copias en el grupo"}
        
        if not keep_copy_ids:
            return {"success": False, "error": "No se seleccionaron copias a conservar"}
        
        # Separar copias a conservar y a eliminar
        keep_set = set(keep_copy_ids)
        copies_to_keep = [c for c in copies if c.id in keep_set]
        copies_to_remove = [c for c in copies if c.id not in keep_set]
        
        if not copies_to_keep:
            return {"success": False, "error": "Ninguna de las copias seleccionadas existe en el grupo"}
        
        removed = []
        errors = []
        
        for copy in copies_to_remove:
            filepath = copy.path
            
            if not filepath or not os.path.exists(filepath):
                errors.append(f"Archivo no encontrado: {filepath}")
                continue
            
            try:
                if trash_enabled:
                    success = move_to_trash(filepath, settings.trash_path)
                else:
                    success = delete_file(filepath)
                
                if success:
                    removed.append(filepath)
                    await session.delete(copy)
                else:
                    errors.append(f"Error al procesar: {filepath}")
            except Exception as e:
                errors.append(f"Error: {filepath} - {str(e)}")
        
        # Marcar grupo como resuelto
        group.status = DuplicateStatus.RESOLVED
        
        await session.commit()
    
    return {
        "success": True,
        "kept": [c.path for c in copies_to_keep],
        "removed": removed,
        "errors": errors,
        "removedCount": len(removed),
        "keptCount": len(copies_to_keep),
    }
