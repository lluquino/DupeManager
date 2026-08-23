"""DupeManager — API: Settings"""

from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def get_settings():
    """Obtiene la configuración actual"""
    # TODO: Hito 2.3 — Implementar settings desde BD
    return {
        "trashEnabled": True,
        "trashRetentionValue": 30,
        "trashRetentionUnit": "days",
        "autoScanEnabled": True,
        "autoScanValue": 7,
        "autoScanUnit": "days",
        "notificationsBrowser": False,
        "notificationsWebhookEnabled": False,
        "notificationsWebhookUrl": "",
        "notificationsEmailEnabled": False,
        "notificationsEmailSmtpHost": "",
        "notificationsEmailSmtpPort": 587,
        "notificationsEmailUsername": "",
        "notificationsEmailPassword": "",
        "notificationsEmailTo": "",
    }


@router.put("")
async def update_settings():
    """Actualiza la configuración"""
    # TODO: Hito 2.3 — Implementar guardar settings
    return {"status": "not_implemented"}


@router.post("/trash/empty")
async def empty_trash():
    """Vacía la papelera de reciclaje"""
    # TODO: Hito 2.2 — Implementar vaciar papelera
    return {"status": "not_implemented"}


@router.post("/rebuild-db")
async def rebuild_db():
    """Reconstruye la base de datos desde cero"""
    # TODO: Hito 2.3 — Implementar rebuild
    return {"status": "not_implemented"}
