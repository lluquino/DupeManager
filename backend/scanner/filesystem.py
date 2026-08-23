"""DupeManager — Acceso a Filesystem (NFS)"""

import os
import stat
from pathlib import Path
from typing import Optional


def get_file_size(filepath: str) -> Optional[float]:
    """
    Obtiene el tamaño de un archivo en bytes.
    
    Retorna None si el archivo no existe o no se puede acceder.
    """
    try:
        return os.path.getsize(filepath)
    except (OSError, IOError):
        return None


def file_exists(filepath: str) -> bool:
    """Verifica si un archivo existe."""
    return os.path.isfile(filepath)


def get_path_for_display(api_path: str) -> str:
    """
    Convierte una ruta de API a una ruta legible.
    
    /media/Series/... → Series/...
    """
    # Eliminar el prefijo /media/ para mostrar
    if api_path.startswith("/media/"):
        return api_path[7:]  # Eliminar "/media/"
    return api_path


def get_filesystem_path(api_path: str, media_path: str = "/media") -> str:
    """
    Convierte una ruta de API a una ruta del filesystem.
    
    Si el container tiene /mnt/stream/media como /media,
    esta función mapea correctamente.
    """
    # En el contexto de la VM, la ruta ya es correcta
    # En el contexto del container, /media ya está montado
    return api_path


def get_trash_path(api_path: str, trash_path: str = "/media/tmp/DupeManager-trash") -> str:
    """
    Calcula la ruta de destino en la papelera para un archivo.
    
    Mantiene la estructura de carpetas original.
    
    Ejemplo:
        /media/Series/Big Bang Theory/Season 1/file.mkv
        → /media/tmp/DupeManager-trash/Series/Big Bang Theory/Season 1/file.mkv
    """
    # Obtener la ruta relativa desde /media
    if api_path.startswith("/media/"):
        relative = api_path[7:]  # Eliminar "/media/"
    else:
        relative = api_path
    
    return os.path.join(trash_path, relative)


def move_to_trash(source_path: str, trash_path: str = "/media/tmp/DupeManager-trash") -> bool:
    """
    Mueve un archivo a la papelera.
    
    Crea la estructura de carpetas si no existe.
    Retorna True si éxito, False si error.
    """
    import shutil
    
    try:
        # Calcular destino
        dest = get_trash_path(source_path, trash_path)
        
        # Crear directorio destino
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        
        # Mover archivo
        shutil.move(source_path, dest)
        
        return True
    except (OSError, IOError) as e:
        print(f"Error moving to trash: {e}")
        return False


def delete_file(filepath: str) -> bool:
    """
    Elimina un archivo permanentemente.
    
    Retorna True si éxito, False si error.
    """
    try:
        os.remove(filepath)
        return True
    except (OSError, IOError) as e:
        print(f"Error deleting file: {e}")
        return False


def empty_trash(trash_path: str = "/media/tmp/DupeManager-trash") -> int:
    """
    Vacía la papelera de reciclaje.
    
    Retorna el número de archivos eliminados.
    """
    import shutil
    
    count = 0
    
    if not os.path.exists(trash_path):
        return 0
    
    for root, dirs, files in os.walk(trash_path, topdown=False):
        for name in files:
            filepath = os.path.join(root, name)
            try:
                os.remove(filepath)
                count += 1
            except (OSError, IOError):
                pass
        
        for name in dirs:
            dirpath = os.path.join(root, name)
            try:
                os.rmdir(dirpath)
            except (OSError, IOError):
                pass
    
    # Intentar eliminar el directorio raíz de la papelera
    try:
        os.rmdir(trash_path)
    except (OSError, IOError):
        pass
    
    return count


def list_files_recursive(directory: str) -> list[str]:
    """
    Lista todos los archivos en un directorio recursivamente.
    
    Retorna lista de rutas absolutas.
    """
    files = []
    
    if not os.path.exists(directory):
        return files
    
    for root, dirs, filenames in os.walk(directory):
        for name in filenames:
            files.append(os.path.join(root, name))
    
    return files
