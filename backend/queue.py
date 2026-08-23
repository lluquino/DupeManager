"""DupeManager — Sistema de Colas para Escaneo en Background"""

import asyncio
from typing import Optional, Callable
from datetime import datetime, timezone

from backend.scanner.detector import run_full_scan


class ScanQueue:
    """Cola simple para escaneo en background"""
    
    def __init__(self):
        self._task: Optional[asyncio.Task] = None
        self._running = False
        self._progress = 0.0
        self._message = "Idle"
        self._current_item = ""
        self._total_items = 0
        self._result = None
        self._error = None
    
    @property
    def running(self) -> bool:
        return self._running
    
    @property
    def progress(self) -> float:
        return self._progress
    
    @property
    def message(self) -> str:
        return self._message
    
    @property
    def current_item(self) -> str:
        return self._current_item
    
    @property
    def total_items(self) -> int:
        return self._total_items
    
    @property
    def result(self) -> Optional[dict]:
        return self._result
    
    @property
    def error(self) -> Optional[str]:
        return self._error
    
    def _progress_callback(self, progress: float, message: str):
        """Callback para actualizar progreso"""
        self._progress = progress
        self._message = message
    
    async def start(self, jellyfin_token: str) -> dict:
        """
        Inicia un escaneo completo en background.
        
        Si ya hay un escaneo en curso, retorna el estado actual.
        """
        if self._running:
            return {
                "status": "already_running",
                "progress": self._progress,
                "message": self._message,
            }
        
        # Limpiar estado anterior
        self._running = True
        self._progress = 0.0
        self._message = "Iniciando escaneo..."
        self._current_item = ""
        self._total_items = 0
        self._result = None
        self._error = None
        
        # Lanzar escaneo en background (no bloquea)
        asyncio.create_task(self._run_scan(jellyfin_token))
        
        return {
            "status": "started",
            "progress": 0,
            "message": "Iniciando escaneo...",
        }
    
    async def _run_scan(self, jellyfin_token: str):
        """Ejecuta el escaneo en background"""
        try:
            self._result = await run_full_scan(
                jellyfin_token,
                progress_callback=self._progress_callback,
            )
            self._message = "Escaneo completado"
            self._progress = 100.0
        except Exception as e:
            self._error = str(e)
            self._message = f"Error: {e}"
        finally:
            self._running = False
    
    def get_status(self) -> dict:
        """Obtiene el estado actual de la cola"""
        return {
            "running": self._running,
            "progress": self._progress,
            "message": self._message,
            "currentItem": self._current_item,
            "totalItems": self._total_items,
            "error": self._error,
        }


# Singleton de la cola
scan_queue = ScanQueue()
