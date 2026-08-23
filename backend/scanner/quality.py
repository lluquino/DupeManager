"""DupeManager — Extracción de Calidad y Scoring"""

import re
from pathlib import Path


# ── Tabla de Scores ───────────────────────────────────────
# Basada en la jerarquía definida por el usuario:
#   10: 1080p HEVC
#    8: 1080p (H264/otros)
#    6: 720p
#    5: 2K / 1440p
#    4: 4K / 2160p
#    2: SD / DVD / 3D
#    0: CAM / TS / TC
#   -1: No definido

RESOLUTION_SCORES = {
    "2160p": 4,
    "4k": 4,
    "uhd": 4,
    "1440p": 5,
    "2k": 5,
    "1080p": 8,
    "720p": 6,
    "480p": 2,
    "sd": 2,
}

CODEC_BONUSES = {
    "hevc": 2,
    "h265": 2,
    "x265": 2,
    "h264": 0,
    "x264": 0,
    "avc": 0,
    "mpeg4": -1,
    "mpeg-4": -1,
    "xvid": -2,
}

SOURCE_BONUSES = {
    "bluray": 1,
    "bdrip": 1,
    "bdremux": 1,
    "remux": 1,
    "web-dl": 0,
    "webdl": 0,
    "webrip": 0,
    "hdrip": -1,
    "hdtv": -1,
    "dvdrip": -2,
    "dvd": -2,
    "microhd": 0,
}

# Codecs de video conocidos
VIDEO_CODECS = {
    "hevc", "h265", "x265",
    "h264", "x264", "avc",
    "mpeg4", "mpeg-4", "xvid",
    "mpeg2", "mpeg-2",
    "vp8", "vp9", "av1",
}

# Resoluciones conocidas
RESOLUTIONS = {
    "2160p", "4k", "uhd",
    "1440p", "2k",
    "1080p",
    "720p",
    "480p",
}


def extract_resolution(filename: str, media_streams: dict | None = None) -> str | None:
    """
    Extrae la resolución del filename o de MediaStreams.
    
    Prioridad:
    1. MediaStreams (más preciso)
    2. Filename
    """
    # Intentar de MediaStreams primero
    if media_streams:
        for stream in media_streams.get("VideoStream", []):
            height = stream.get("Height")
            if height:
                if height >= 2160:
                    return "2160p"
                elif height >= 1440:
                    return "1440p"
                elif height >= 1080:
                    return "1080p"
                elif height >= 720:
                    return "720p"
                elif height >= 480:
                    return "480p"
    
    # Buscar en filename
    fname = Path(filename).name.lower()
    
    # Buscar resolución exacta
    for res in RESOLUTIONS:
        if re.search(rf'\b{re.escape(res)}\b', fname):
            return res
    
    # Buscar patrones como "1920x1080"
    m = re.search(r'(\d{3,4})x(\d{3,4})', fname)
    if m:
        height = int(m.group(2))
        if height >= 2160:
            return "2160p"
        elif height >= 1440:
            return "1440p"
        elif height >= 1080:
            return "1080p"
        elif height >= 720:
            return "720p"
        elif height >= 480:
            return "480p"
    
    return None


def extract_codec(filename: str, media_streams: dict | None = None) -> str | None:
    """
    Extrae el codec de video del filename o de MediaStreams.
    """
    # Intentar de MediaStreams primero
    if media_streams:
        for stream in media_streams.get("VideoStream", []):
            codec = stream.get("Codec", "").lower()
            if codec:
                return codec
    
    # Buscar en filename
    fname = Path(filename).name.lower()
    
    for codec in VIDEO_CODECS:
        if re.search(rf'\b{re.escape(codec)}\b', fname):
            return codec
    
    return None


def extract_source(filename: str) -> str | None:
    """Extrae la fuente del filename."""
    fname = Path(filename).name.lower()
    
    for source in SOURCE_BONUSES:
        if re.search(rf'\b{re.escape(source)}\b', fname):
            return source
    
    return None


def is_3d(filename: str) -> bool:
    """Detecta si el archivo es 3D."""
    fname = Path(filename).name.lower()
    return bool(re.search(r'\b(3d|sbs|half-ou|stereoscopic)\b', fname))


def calculate_quality_score(
    filename: str,
    size: float = 0,
    media_streams: dict | None = None,
) -> dict:
    """
    Calcula el score de calidad de un archivo.
    
    Returns:
        dict con:
            - score: puntuación total
            - resolution: resolución detectada
            - codec: codec detectado
            - source: fuente detectada
            - is_3d: si es 3D
    """
    resolution = extract_resolution(filename, media_streams)
    codec = extract_codec(filename, media_streams)
    source = extract_source(filename)
    is_3d_file = is_3d(filename)
    
    # Si es 3D, score forzado a 2
    if is_3d_file:
        return {
            "score": 2,
            "resolution": resolution,
            "codec": codec,
            "source": source,
            "is_3d": True,
        }
    
    # Calcular score base desde resolución
    score = -1  # Default: no definido
    if resolution:
        score = RESOLUTION_SCORES.get(resolution.lower(), -1)
    
    # Aplicar bonus de codec
    if codec:
        codec_lower = codec.lower()
        score += CODEC_BONUSES.get(codec_lower, 0)
    
    # Aplicar bonus de fuente
    if source:
        source_lower = source.lower()
        score += SOURCE_BONUSES.get(source_lower, 0)
    
    # En empate, usar tamaño como desempate (mayor = mejor bitrate = mejor calidad)
    # Esto se maneja externamente al comparar scores
    
    return {
        "score": score,
        "resolution": resolution,
        "codec": codec,
        "source": source,
        "is_3d": False,
    }


def get_quality_label(score: int) -> str:
    """Retorna una etiqueta legible del score."""
    if score >= 10:
        return "Excelente"
    elif score >= 8:
        return "Muy buena"
    elif score >= 6:
        return "Buena"
    elif score >= 4:
        return "Regular"
    elif score >= 2:
        return "Baja"
    elif score >= 0:
        return "Muy baja"
    else:
        return "Desconocida"
