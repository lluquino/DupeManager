"""DupeManager — Cliente HTTP para Jellyfin"""

import httpx
from typing import Optional, Any
from backend.config import settings


class JellyfinClient:
    """Cliente asíncrono para la API de Jellyfin"""

    def __init__(self):
        self.base_url = settings.jellyfin_url.rstrip("/")
        self.api_key = settings.jellyfin_api_key
        self.headers = {
            "X-Emby-Authorization": 'MediaBrowser Client="DupeManager", Device="Linux", DeviceId="dupemanager", Version="1.0.0"',
            "Content-Type": "application/json",
        }

    async def _request(
        self,
        method: str,
        path: str,
        token: Optional[str] = None,
        use_api_key: bool = True,
        **kwargs,
    ) -> dict[str, Any]:
        """Realiza una petición a la API de Jellyfin"""
        headers = {}
        
        # Añadir Authorization header
        if token:
            headers["X-Emby-Token"] = token
        elif use_api_key and self.api_key:
            # Usar api_key como header si no hay token de usuario
            pass  # api_key va como query param
        
        headers["X-Emby-Authorization"] = 'MediaBrowser Client="DupeManager", Device="Linux", DeviceId="dupemanager", Version="1.0.0"'

        url = f"{self.base_url}{path}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(method, url, headers=headers, **kwargs)
            response.raise_for_status()
            return response.json()

    # ── Auth ──────────────────────────────────────────────

    async def authenticate(self, username: str, password: str) -> dict:
        """Autentica contra Jellyfin y devuelve token"""
        return await self._request(
            "POST",
            "/Users/AuthenticateByName",
            json={"Username": username, "Pw": password},
        )

    async def get_user(self, user_id: str, token: str) -> dict:
        """Obtiene el perfil de un usuario"""
        return await self._request("GET", f"/Users/{user_id}", token=token)

    # ── Items ─────────────────────────────────────────────

    async def get_episodes(
        self,
        token: str = None,
        limit: int = 500,
        start_index: int = 0,
    ) -> dict:
        """Obtiene todos los episodios"""
        return await self._request(
            "GET",
            "/Items",
            token=token,
            params={
                "api_key": self.api_key,
                "Recursive": "true",
                "IncludeItemTypes": "Episode",
                "Fields": "Path,MediaStreams,Size,ProductionYear,SeriesName,SeasonIndexNumber,IndexNumber,LocationType",
                "Limit": limit,
                "StartIndex": start_index,
            },
        )

    async def get_movies(
        self,
        token: str = None,
        limit: int = 500,
        start_index: int = 0,
    ) -> dict:
        """Obtiene todas las películas"""
        return await self._request(
            "GET",
            "/Items",
            token=token,
            params={
                "api_key": self.api_key,
                "Recursive": "true",
                "IncludeItemTypes": "Movie",
                "Fields": "Path,MediaStreams,Size,ProductionYear,LocationType",
                "Limit": limit,
                "StartIndex": start_index,
            },
        )

    async def get_item(self, item_id: str, token: str) -> dict:
        """Obtiene un item específico"""
        return await self._request(
            "GET",
            f"/Items/{item_id}",
            token=token,
            params={"api_key": self.api_key, "Fields": "MediaStreams"},
        )

    # ── System ────────────────────────────────────────────

    async def get_system_info(self) -> dict:
        """Obtiene info del servidor (público, no requiere auth)"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{self.base_url}/System/Info/Public")
            response.raise_for_status()
            return response.json()


# Singleton
jellyfin = JellyfinClient()
