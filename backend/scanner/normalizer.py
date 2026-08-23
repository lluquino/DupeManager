"""DupeManager — Normalización de Nombres"""

import unicodedata
import re
from pathlib import Path


def normalize_name(name: str) -> str:
    """
    Normaliza un nombre para comparación.
    
    - Elimina acentos y diacríticos
    - Convierte a minúsculas
    - Elimina puntuación
    - Elimina espacios múltiples
    
    Ejemplos:
        "La Casa del Dragón" → "la casa del dragon"
        "The Big Bang Theory" → "the big bang theory"
        "ONE PIECE" → "one piece"
    """
    if not name:
        return ""
    
    # Normalizar Unicode (elimina acentos)
    name = unicodedata.normalize("NFKD", name)
    name = "".join(c for c in name if not unicodedata.combining(c))
    
    # Minúsculas
    name = name.lower()
    
    # Eliminar puntuación (mantener espacios y números)
    name = re.sub(r"[^\w\s]", " ", name)
    
    # Eliminar espacios múltiples
    name = re.sub(r"\s+", " ", name).strip()
    
    return name


def normalize_series_name(name: str) -> str:
    """
    Normaliza nombre de serie para agrupación.
    
    Elimina suffixes comunes como "720P", "1080P", etc.
    """
    name = normalize_name(name)
    
    # Eliminar suffixes de calidad que pueden aparecer en el nombre de la serie
    quality_suffixes = [
        r"\b\d{3,4}p\b",       # 720p, 1080p, 2160p
        r"\b4k\b",             # 4K
        r"\bhd\b",             # HD
        r"\bsd\b",             # SD
        r"\bbluray\b",         # BluRay
        r"\bdvdrip\b",         # DVDRip
        r"\bweb-dl\b",         # WEB-DL
        r"\bwebrip\b",         # WEBRip
    ]
    
    for suffix in quality_suffixes:
        name = re.sub(suffix, "", name, flags=re.IGNORECASE)
    
    # Limpiar espacios extras
    name = re.sub(r"\s+", " ", name).strip()
    
    return name


def extract_episode_from_filename(filepath: str) -> int | None:
    """
    Extrae el número de episodio del filename.
    
    Formatos soportados:
        - "- NN " o "- NN [" (ej: "Series - 05 [1080p].mkv")
        - s01e05 (ej: "Series s01e05.mkv")
        - S01E05 (ej: "Series S01E05.mkv")
        - "Episode NN" (ej: "Episode 5.mkv")
    """
    fname = Path(filepath).name
    
    # Formato: - NN [ o - NN .
    m = re.search(r'-\s*(\d{1,4})\s*[\[\.\s]', fname)
    if m:
        return int(m.group(1))
    
    # Formato: s01e05 o S01E05
    m = re.search(r's(\d+)e(\d+)', fname, re.IGNORECASE)
    if m:
        return int(m.group(2))
    
    # Formato: Episode NN
    m = re.search(r'episode\s+(\d{1,4})', fname, re.IGNORECASE)
    if m:
        return int(m.group(1))
    
    return None


def extract_season_from_path(filepath: str) -> int | None:
    """
    Extrae el número de temporada de la ruta.
    
    Formatos soportados:
        - Season 1/
        - Season 01/
        - Temporada 1/
        - S01/
        - s01/
    """
    # Buscar en la ruta completa
    m = re.search(r'season\s+(\d+)', filepath, re.IGNORECASE)
    if m:
        return int(m.group(1))
    
    m = re.search(r'temporada\s+(\d+)', filepath, re.IGNORECASE)
    if m:
        return int(m.group(1))
    
    m = re.search(r'[/\\]s(\d+)[/\\]', filepath, re.IGNORECASE)
    if m:
        return int(m.group(1))
    
    return None


def extract_series_name_from_path(filepath: str) -> str | None:
    """
    Extrae el nombre de la serie de la ruta.
    
    Asume estructura: /media/Series/Series Name/Season X/file.mkv
    """
    parts = Path(filepath).parts
    
    # Buscar el índice de "Series" o "Anime" en la ruta
    for i, part in enumerate(parts):
        if part.lower() in ("series", "anime", "seriesanimacion"):
            if i + 1 < len(parts):
                return parts[i + 1]
    
    return None


def extract_movie_name_from_filename(filename: str) -> str:
    """
    Extrae el nombre de la película del filename.
    
    Elimina calidad, codec, año, etc.
    
    Ejemplo:
        "El atlas de las nubes [MicroHD][E-AC3 5.1 Castellano][ES-EN] (2024)"
        → "El atlas de las nubes"
    """
    name = filename
    
    # Eliminar extensión
    name = Path(name).stem
    
    # Eliminar año entre paréntesis al final
    name = re.sub(r'\s*\(\d{4}\)\s*$', '', name)
    
    # Eliminar calidad entre corchetes
    name = re.sub(r'\[[^\]]*\]', '', name)
    
    # Eliminar calidad sin corchetes
    quality_patterns = [
        r'\b\d{3,4}p\b',
        r'\b4k\b',
        r'\buhd\b',
        r'\bhd\b',
        r'\bsd\b',
        r'\bbluray\b',
        r'\bweb-dl\b',
        r'\bwebrip\b',
        r'\bdvdrip\b',
        r'\bhdtv\b',
        r'\bhdrip\b',
        r'\bmicrohd\b',
        r'\bremux\b',
    ]
    
    for pattern in quality_patterns:
        name = re.sub(pattern, '', name, flags=re.IGNORECASE)
    
    # Limpiar espacios extras
    name = re.sub(r'\s+', ' ', name).strip()
    
    # Eliminar guiones al final
    name = re.sub(r'\s*-\s*$', '', name)
    
    return name


def extract_year_from_filename(filename: str) -> int | None:
    """Extrae el año del filename."""
    # Buscar año entre paréntesis
    m = re.search(r'\((\d{4})\)', filename)
    if m:
        year = int(m.group(1))
        if 1900 <= year <= 2099:
            return year
    
    return None
