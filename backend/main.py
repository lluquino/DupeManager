"""DupeManager — FastAPI Application"""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from backend.config import settings
from backend.database import init_db


async def trash_cleanup_loop():
    """Background task para limpieza periódica de la papelera"""
    while True:
        await asyncio.sleep(3600)  # Cada hora
        try:
            from backend.actions.trash import trash_scheduler
            if settings.trash_enabled:
                trash_scheduler.run_cleanup()
        except Exception as e:
            print(f"Error en limpieza de papelera: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    await init_db()
    print(f"✅ DupeManager started on {settings.host}:{settings.port}")
    
    # Iniciar cleanup loop en background
    task = asyncio.create_task(trash_cleanup_loop())
    
    yield
    
    # Shutdown
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    print("👋 DupeManager shutting down")


app = FastAPI(
    title="DupeManager",
    description="Gestor de duplicados de Jellyfin",
    version="1.0.0",
    lifespan=lifespan,
)


# ── API Routes ────────────────────────────────────────────

from backend.api.auth import router as auth_router
from backend.api.dashboard import router as dashboard_router
from backend.api.scan import router as scan_router
from backend.api.episodes import router as episodes_router
from backend.api.movies import router as movies_router
from backend.api.ignored import router as ignored_router
from backend.api.settings import router as settings_router

app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(scan_router, prefix="/api/scan", tags=["scan"])
app.include_router(episodes_router, prefix="/api/episodes", tags=["episodes"])
app.include_router(movies_router, prefix="/api/movies", tags=["movies"])
app.include_router(ignored_router, prefix="/api/ignored", tags=["ignored"])
app.include_router(settings_router, prefix="/api/settings", tags=["settings"])


# ── Static Files (Frontend) ──────────────────────────────

frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/css", StaticFiles(directory=frontend_dir / "css"), name="css")
    app.mount("/js", StaticFiles(directory=frontend_dir / "js"), name="js")
    app.mount("/assets", StaticFiles(directory=frontend_dir / "assets"), name="assets")

    @app.get("/")
    async def serve_index():
        return FileResponse(frontend_dir / "index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )
