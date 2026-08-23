"""DupeManager — Servicio de Papelera con Auto-limpieza"""

import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from backend.config import settings


def get_retention_seconds() -> int:
    """
    Calcula los segundos de retención según la configuración.
    
    Soporta: minutes, hours, days, weeks, months
    """
    value = settings.trash_retention_value
    unit = settings.trash_retention_unit
    
    multipliers = {
        "minutes": 60,
        "hours": 3600,
        "days": 86400,
        "weeks": 604800,
        "months": 2592000,  # 30 días
    }
    
    return value * multipliers.get(unit, 86400)


def cleanup_old_trash_files(trash_path: str = None) -> dict:
    """
    Elimina archivos de la papelera que superen el tiempo de retención.
    
    Returns:
        dict con estadísticas de la limpieza
    """
    if trash_path is None:
        trash_path = settings.trash_path
    
    stats = {"deleted": 0, "errors": 0, "freed_bytes": 0}
    
    if not os.path.exists(trash_path):
        return stats
    
    retention_seconds = get_retention_seconds()
    cutoff_time = time.time() - retention_seconds
    
    for root, dirs, files in os.walk(trash_path, topdown=False):
        for name in files:
            filepath = os.path.join(root, name)
            try:
                # Obtener tiempo de última modificación
                mtime = os.path.getmtime(filepath)
                
                if mtime < cutoff_time:
                    size = os.path.getsize(filepath)
                    os.remove(filepath)
                    stats["deleted"] += 1
                    stats["freed_bytes"] += size
            except (OSError, IOError):
                stats["errors"] += 1
        
        # Eliminar directorios vacíos
        for name in dirs:
            dirpath = os.path.join(root, name)
            try:
                if not os.listdir(dirpath):
                    os.rmdir(dirpath)
            except (OSError, IOError):
                pass
    
    # Intentar eliminar el directorio raíz si está vacío
    try:
        if not os.listdir(trash_path):
            os.rmdir(trash_path)
    except (OSError, IOError):
        pass
    
    return stats


def empty_trash(trash_path: str = None) -> dict:
    """
    Vacía toda la papelera de reciclaje.
    
    Returns:
        dict con estadísticas
    """
    if trash_path is None:
        trash_path = settings.trash_path
    
    stats = {"deleted": 0, "errors": 0, "freed_bytes": 0}
    
    if not os.path.exists(trash_path):
        return stats
    
    for root, dirs, files in os.walk(trash_path, topdown=False):
        for name in files:
            filepath = os.path.join(root, name)
            try:
                size = os.path.getsize(filepath)
                os.remove(filepath)
                stats["deleted"] += 1
                stats["freed_bytes"] += size
            except (OSError, IOError):
                stats["errors"] += 1
        
        for name in dirs:
            dirpath = os.path.join(root, name)
            try:
                os.rmdir(dirpath)
            except (OSError, IOError):
                pass
    
    try:
        os.rmdir(trash_path)
    except (OSError, IOError):
        pass
    
    return stats


def get_trash_info(trash_path: str = None) -> dict:
    """
    Obtiene información sobre el estado de la papelera.
    
    Returns:
        dict con stats de la papelera
    """
    if trash_path is None:
        trash_path = settings.trash_path
    
    info = {
        "exists": False,
        "fileCount": 0,
        "totalSize": 0,
        "oldestFile": None,
        "newestFile": None,
    }
    
    if not os.path.exists(trash_path):
        return info
    
    info["exists"] = True
    oldest_time = float("inf")
    newest_time = 0
    
    for root, dirs, files in os.walk(trash_path):
        for name in files:
            filepath = os.path.join(root, name)
            try:
                size = os.path.getsize(filepath)
                mtime = os.path.getmtime(filepath)
                
                info["fileCount"] += 1
                info["totalSize"] += size
                
                if mtime < oldest_time:
                    oldest_time = mtime
                    info["oldestFile"] = datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()
                
                if mtime > newest_time:
                    newest_time = mtime
                    info["newestFile"] = datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()
            except (OSError, IOError):
                pass
    
    return info


def list_trash_files(trash_path: str = None) -> list[dict]:
    """
    Lista los archivos en la papelera con su tamaño y tiempo hasta borrado.
    
    Returns:
        Lista de dicts con name, path, size, modified, deleteAt, timeRemaining
    """
    if trash_path is None:
        trash_path = settings.trash_path
    
    files = []
    
    if not os.path.exists(trash_path):
        return files
    
    # Get retention settings
    retention_value = settings.trash_retention_value
    retention_unit = settings.trash_retention_unit
    
    # Calculate retention in seconds
    unit_seconds = {
        "minutes": 60,
        "hours": 3600,
        "days": 86400,
        "weeks": 604800,
        "months": 2592000,  # 30 days
    }
    retention_seconds = retention_value * unit_seconds.get(retention_unit, 86400)
    
    now = datetime.now(timezone.utc)
    
    for root, dirs, filenames in os.walk(trash_path):
        for name in filenames:
            filepath = os.path.join(root, name)
            try:
                size = os.path.getsize(filepath)
                mtime = os.path.getmtime(filepath)
                modified = datetime.fromtimestamp(mtime, tz=timezone.utc)
                rel_path = os.path.relpath(filepath, trash_path)
                
                # Calculate deletion time
                delete_at = modified + timedelta(seconds=retention_seconds)
                
                # Calculate time remaining
                time_remaining = delete_at - now
                remaining_seconds = max(0, time_remaining.total_seconds())
                
                # Format time remaining
                if remaining_seconds <= 0:
                    time_remaining_str = "Borrado pronto"
                elif remaining_seconds < 3600:
                    minutes = int(remaining_seconds // 60)
                    time_remaining_str = f"{minutes} min"
                elif remaining_seconds < 86400:
                    hours = int(remaining_seconds // 3600)
                    time_remaining_str = f"{hours}h"
                else:
                    days = int(remaining_seconds // 86400)
                    if days >= 30:
                        months = days // 30
                        remaining_days = days % 30
                        if remaining_days > 0:
                            time_remaining_str = f"{months}m {remaining_days}d"
                        else:
                            time_remaining_str = f"{months} meses"
                    elif days >= 7:
                        weeks = days // 7
                        remaining_days = days % 7
                        if remaining_days > 0:
                            time_remaining_str = f"{weeks}sem {remaining_days}d"
                        else:
                            time_remaining_str = f"{weeks} semanas"
                    else:
                        time_remaining_str = f"{days} días"
                
                files.append({
                    "name": name,
                    "path": rel_path,
                    "size": size,
                    "modified": modified.isoformat(),
                    "deleteAt": delete_at.isoformat(),
                    "timeRemaining": time_remaining_str,
                    "deleteToday": delete_at.date() == now.date(),
                    "deleteTime": delete_at.strftime("%H:%M") if delete_at.date() == now.date() else None,
                })
            except (OSError, IOError):
                pass
    
    # Sort by deletion time (soonest first)
    files.sort(key=lambda f: f["deleteAt"])
    
    return files


def restore_file(rel_path: str, trash_path: str = None) -> dict:
    """
    Restaura un archivo de la papelera a su ubicación original.
    
    Args:
        rel_path: Ruta relativa del archivo dentro de la papelera
        trash_path: Ruta base de la papelera
    
    Returns:
        dict con resultado de la operación
    """
    import shutil
    
    if trash_path is None:
        trash_path = settings.trash_path
    
    source = os.path.join(trash_path, rel_path)
    
    if not os.path.exists(source):
        return {"success": False, "error": "Archivo no encontrado en la papelera"}
    
    # Reconstruct original path
    # trash_path/media/... -> /media/...
    media_path = settings.media_path
    dest = os.path.join(media_path, rel_path)
    
    try:
        # Create destination directory if needed
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.move(source, dest)
        return {"success": True, "restored": rel_path, "destination": dest}
    except Exception as e:
        return {"success": False, "error": str(e)}


def delete_file_from_trash(rel_path: str, trash_path: str = None) -> dict:
    """
    Elimina permanentemente un archivo de la papelera.
    
    Args:
        rel_path: Ruta relativa del archivo dentro de la papelera
    
    Returns:
        dict con resultado de la operación
    """
    if trash_path is None:
        trash_path = settings.trash_path
    
    filepath = os.path.join(trash_path, rel_path)
    
    if not os.path.exists(filepath):
        return {"success": False, "error": "Archivo no encontrado"}
    
    try:
        size = os.path.getsize(filepath)
        os.remove(filepath)
        return {"success": True, "deleted": rel_path, "freedBytes": size}
    except Exception as e:
        return {"success": False, "error": str(e)}


class TrashCleanupScheduler:
    """
    Scheduler para limpieza automática de la papelera.
    
    Se ejecuta periódicamente (cada hora) y elimina archivos
    que superen el tiempo de retención configurado.
    """
    
    def __init__(self):
        self._running = False
        self._last_cleanup = None
        self._next_cleanup = None
    
    @property
    def running(self) -> bool:
        return self._running
    
    @property
    def last_cleanup(self) -> Optional[datetime]:
        return self._last_cleanup
    
    @property
    def next_cleanup(self) -> Optional[datetime]:
        return self._next_cleanup
    
    def run_cleanup(self) -> dict:
        """Ejecuta la limpieza de la papelera."""
        if self._running:
            return {"status": "already_running"}
        
        self._running = True
        
        try:
            if settings.trash_enabled:
                stats = cleanup_old_trash_files()
                self._last_cleanup = datetime.now(timezone.utc)
                self._next_cleanup = self._last_cleanup + timedelta(hours=1)
                return {"status": "completed", "stats": stats}
            else:
                return {"status": "disabled"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
        finally:
            self._running = False


# Singleton
trash_scheduler = TrashCleanupScheduler()
