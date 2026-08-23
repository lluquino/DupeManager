"""DupeManager — API: Settings"""

from fastapi import APIRouter, Depends
from backend.auth import get_current_user
from backend.actions.trash import empty_trash, get_trash_info
from backend.settings_service import get_all_settings, update_settings
from backend.notifications.service import send_test_notification

router = APIRouter()


@router.get("")
async def get_settings(user: dict = Depends(get_current_user)):
    """Obtiene la configuración actual"""
    settings = await get_all_settings()
    return settings


@router.put("")
async def update_settings_endpoint(body: dict, user: dict = Depends(get_current_user)):
    """Actualiza la configuración"""
    # Filtrar solo campos válidos
    valid_keys = [
        "trashEnabled", "trashRetentionValue", "trashRetentionUnit",
        "autoScanEnabled", "autoScanValue", "autoScanUnit",
        "notificationsBrowser", "notificationsWebhookEnabled", "notificationsWebhookUrl",
        "notificationsEmailEnabled", "notificationsEmailSmtpHost", "notificationsEmailSmtpPort",
        "notificationsEmailUsername", "notificationsEmailPassword", "notificationsEmailTo",
    ]
    
    # Convertir de camelCase a snake_case
    settings_to_update = {}
    for key, value in body.items():
        if key in valid_keys:
            snake_key = ''.join(['_' + c.lower() if c.isupper() else c for c in key]).lstrip('_')
            settings_to_update[snake_key] = value
    
    if settings_to_update:
        await update_settings(settings_to_update)
    
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
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    return {"success": True, "message": "Base de datos reconstruida"}


@router.post("/notifications/test-webhook")
async def test_webhook(user: dict = Depends(get_current_user)):
    """Envía un webhook de prueba"""
    result = await send_test_notification("webhook")
    return result


@router.post("/notifications/test-email")
async def test_email(user: dict = Depends(get_current_user)):
    """Envía un email de prueba"""
    result = await send_test_notification("email")
    return result
