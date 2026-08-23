"""DupeManager — API: Settings"""

from fastapi import APIRouter, Depends
from backend.auth import get_current_user
from backend.actions.trash import empty_trash, get_trash_info

router = APIRouter()


@router.get("")
async def get_settings(user: dict = Depends(get_current_user)):
    """Obtiene la configuración actual"""
    from backend.config import settings
    
    return {
        "trashEnabled": settings.trash_enabled,
        "trashRetentionValue": settings.trash_retention_value,
        "trashRetentionUnit": settings.trash_retention_unit,
        "autoScanEnabled": settings.auto_scan_enabled,
        "autoScanValue": settings.auto_scan_value,
        "autoScanUnit": settings.auto_scan_unit,
        "notificationsBrowser": settings.notifications_browser,
        "notificationsWebhookEnabled": settings.notifications_webhook_enabled,
        "notificationsWebhookUrl": settings.notifications_webhook_url,
        "notificationsEmailEnabled": settings.notifications_email_enabled,
        "notificationsEmailSmtpHost": settings.notifications_email_smtp_host,
        "notificationsEmailSmtpPort": settings.notifications_email_smtp_port,
        "notificationsEmailUsername": settings.notifications_email_username,
        "notificationsEmailPassword": settings.notifications_email_password,
        "notificationsEmailTo": settings.notifications_email_to,
    }


@router.put("")
async def update_settings(body: dict, user: dict = Depends(get_current_user)):
    """Actualiza la configuración"""
    # TODO: Hito 2.3 — Guardar en BD
    return {"success": True, "message": "Configuración actualizada"}


@router.post("/trash/empty")
async def empty_trash_endpoint(user: dict = Depends(get_current_user)):
    """Vacía la papelera de reciclaje"""
    stats = empty_trash()
    return {
        "success": True,
        "deleted": stats["deleted"],
        "freedBytes": stats["freed_bytes"],
        "errors": stats["errors"],
    }


@router.get("/trash/info")
async def get_trash_info_endpoint(user: dict = Depends(get_current_user)):
    """Obtiene información sobre la papelera"""
    info = get_trash_info()
    return info


@router.post("/rebuild-db")
async def rebuild_db(user: dict = Depends(get_current_user)):
    """Reconstruye la base de datos desde cero"""
    from backend.database import engine, Base
    from backend.config import settings
    
    async with engine.begin() as conn:
        # Eliminar tablas existentes
        await conn.run_sync(Base.metadata.drop_all)
        # Recrear tablas
        await conn.run_sync(Base.metadata.create_all)
    
    return {"success": True, "message": "Base de datos reconstruida"}
