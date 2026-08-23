"""DupeManager — Helper para formatear datos de copias"""

import json
from typing import Optional


def parse_media_streams(media_streams_json: Optional[str]) -> list[dict]:
    """Parsea el JSON de media streams y retorna lista de streams"""
    if not media_streams_json:
        return []
    try:
        streams = json.loads(media_streams_json)
        if isinstance(streams, list):
            return streams
        return []
    except (json.JSONDecodeError, TypeError):
        return []


def format_copy(copy) -> dict:
    """
    Formatea una copia para la respuesta API.
    
    Incluye mediaStreams parseado con información de audio y subtítulos.
    """
    streams = parse_media_streams(copy.media_streams_json)
    
    # Extraer pistas de audio
    audio_tracks = []
    for s in streams:
        if s.get("Type") == "Audio":
            track = {
                "codec": s.get("Codec", ""),
                "language": s.get("Language", ""),
                "title": s.get("Title", ""),
                "channels": s.get("Channels"),
                "channelLayout": s.get("ChannelLayout", ""),
                "isDefault": s.get("IsDefault", False),
            }
            audio_tracks.append(track)
    
    # Extraer pistas de subtítulos
    subtitle_tracks = []
    for s in streams:
        if s.get("Type") == "Subtitle":
            track = {
                "codec": s.get("Codec", ""),
                "language": s.get("Language", ""),
                "title": s.get("Title", ""),
                "isDefault": s.get("IsDefault", False),
                "isForced": s.get("IsForced", False),
            }
            subtitle_tracks.append(track)
    
    # Extraer info de video
    video_info = {}
    for s in streams:
        if s.get("Type") == "Video":
            video_info = {
                "codec": s.get("Codec", ""),
                "width": s.get("Width"),
                "height": s.get("Height"),
            }
            break
    
    return {
        "id": copy.id,
        "jellyfinItemId": copy.jellyfin_item_id,
        "path": copy.path,
        "filename": copy.filename,
        "size": copy.size,
        "resolution": copy.resolution,
        "codec": copy.codec,
        "qualityScore": copy.quality_score,
        "isBest": copy.is_best,
        "audioTracks": audio_tracks,
        "subtitleTracks": subtitle_tracks,
        "videoInfo": video_info,
        # Jellyfin metadata from parent group
        "seriesName": getattr(copy, '_series_name', None),
        "seriesId": getattr(copy, '_series_id', None),
        "seasonNumber": getattr(copy, '_season_number', None),
        "episodeNumber": getattr(copy, '_episode_number', None),
        "movieName": getattr(copy, '_movie_name', None),
        "movieId": getattr(copy, '_movie_id', None),
        "movieYear": getattr(copy, '_movie_year', None),
    }
