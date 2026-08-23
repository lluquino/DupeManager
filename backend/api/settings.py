"""DupeManager — API: Settings"""

from fastapi import APIRouter, Depends
from backend.auth import get_current_user
from backend.actions.trash import empty_trash, get_trash_info, list_trash_files, restore_file, delete_file_from_trash
from backend.settings_service import get_all_settings, update_settings
from backend.notifications.service import send_test_notification

router = APIRouter()


@router.get("")
async def get_settings(user: dict = Depends(get_current_user)):
    """Obtiene la configuración actual"""
    snake_settings = await get_all_settings()
    
    # Convert snake_case to camelCase for frontend
    camel_settings = {}
    for key, value in snake_settings.items():
        parts = key.split('_')
        camel_key = parts[0] + ''.join(p.capitalize() for p in parts[1:])
        camel_settings[camel_key] = value
    
    # Add last scan info from database
    from backend.database import async_session, ScanStatus
    from sqlalchemy import select
    from datetime import datetime, timedelta, timezone
    
    async with async_session() as session:
        result = await session.execute(select(ScanStatus).limit(1))
        scan_status = result.scalar_one_or_none()
        
        if scan_status and scan_status.last_scan_at:
            camel_settings["lastAutoScan"] = scan_status.last_scan_at.isoformat()
            
            # Calculate next scan based on interval
            if camel_settings.get("autoScanEnabled"):
                value = camel_settings.get("autoScanValue", 7)
                unit = camel_settings.get("autoScanUnit", "days")
                
                multipliers = {
                    "minutes": timedelta(minutes=value),
                    "hours": timedelta(hours=value),
                    "days": timedelta(days=value),
                    "weeks": timedelta(weeks=value),
                    "months": timedelta(days=value * 30),
                }
                
                delta = multipliers.get(unit, timedelta(days=value))
                next_scan = scan_status.last_scan_at + delta
                camel_settings["nextAutoScan"] = next_scan.isoformat()
            else:
                camel_settings["nextAutoScan"] = None
        else:
            camel_settings["lastAutoScan"] = None
            camel_settings["nextAutoScan"] = None
    
    return camel_settings


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
    """Obtiene información sobre la papelera incluyendo lista de archivos"""
    info = get_trash_info()
    info["files"] = list_trash_files()
    return info


@router.post("/trash/restore")
async def restore_trash_file(body: dict, user: dict = Depends(get_current_user)):
    """Restaura un archivo de la papelera a su ubicación original"""
    rel_path = body.get("path")
    if not rel_path:
        return {"success": False, "error": "Ruta del archivo no proporcionada"}
    
    result = restore_file(rel_path)
    return result


@router.post("/trash/delete")
async def delete_trash_file(body: dict, user: dict = Depends(get_current_user)):
    """Elimina permanentemente un archivo de la papelera"""
    rel_path = body.get("path")
    if not rel_path:
        return {"success": False, "error": "Ruta del archivo no proporcionada"}
    
    result = delete_file_from_trash(rel_path)
    return result


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
