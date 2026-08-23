"""DupeManager — Sistema de Colas para Escaneo en Background"""

import asyncio
from typing import Optional
from datetime import datetime, timezone

from backend.scanner.detector import run_full_scan


class ScanQueue:
    """Cola simple para escaneo en background"""
    
    def __init__(self):
        self._task: Optional[asyncio.Task] = None
        self._cancelled = False
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
    
    def _progress_callback(self, progress: float, message: str):
        """Callback para actualizar progreso"""
        if self._cancelled:
            raise asyncio.CancelledError("Scan cancelled by user")
        self._progress = progress
        self._message = message
    
    def cancel(self) -> dict:
        """
        Cancela el escaneo en curso.
        Retorna el resultado de la cancelación.
        """
        if not self._running:
            return {"success": False, "message": "No hay escaneo en curso"}
        
        self._cancelled = True
        
        if self._task and not self._task.done():
            self._task.cancel()
        
        return {"success": True, "message": "Escaneo cancelado"}
    
    async def start(self, jellyfin_token: str) -> dict:
        """
        Inicia un escaneo completo en background.
        Si hay uno en curso, lo cancela primero.
        """
        # Cancelar scan anterior si existe
        if self._running:
            self.cancel()
            # Esperar un poco a que se cancele
            await asyncio.sleep(0.5)
        
        # Limpiar estado
        self._cancelled = False
        self._running = True
        self._progress = 0.0
        self._message = "Iniciando escaneo..."
        self._current_item = ""
        self._total_items = 0
        self._result = None
        self._error = None
        
        # Lanzar escaneo en background
        self._task = asyncio.create_task(self._run_scan(jellyfin_token))
        
        return {
            "status": "started",
            "progress": 0,
            "message": "Iniciando escaneo...",
        }
    
    async def _run_scan(self, jellyfin_token: str):
        """Ejecuta el escaneo en background"""
        try:
            print(f"[QUEUE] Starting scan...", flush=True)
            self._result = await run_full_scan(
                jellyfin_token,
                progress_callback=self._progress_callback,
            )
            print(f"[QUEUE] Scan completed", flush=True)
            self._message = "Escaneo completado"
            self._progress = 100.0
        except asyncio.CancelledError:
            print(f"[QUEUE] Scan cancelled", flush=True)
            self._message = "Escaneo cancelado"
            self._error = None
        except Exception as e:
            import traceback
            print(f"[QUEUE] Scan error: {e}", flush=True)
            traceback.print_exc()
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
