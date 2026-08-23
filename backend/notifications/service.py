"""DupeManager — Servicio Principal de Notificaciones"""

from backend.notifications.push import send_push_notification
from backend.notifications.webhook import send_webhook, send_duplicate_notification
from backend.notifications.email import send_email, send_duplicate_email
from backend.settings_service import get_all_settings


async def notify_new_duplicates(
    duplicates_found: int,
    episode_groups: int = 0,
    movie_groups: int = 0,
    details: str = "",
) -> dict:
    """
    Envía notificaciones sobre nuevos duplicados detectados.
    
    Usa todos los métodos habilitados (push, webhook, email).
    
    Returns:
        dict con resultados de cada método
    """
    settings = await get_all_settings()
    results = {}
    
    # Construir detalles
    if not details:
        parts = []
        if episode_groups > 0:
            parts.append(f"{episode_groups} grupos de episodios")
        if movie_groups > 0:
            parts.append(f"{movie_groups} grupos de películas")
        if parts:
            details = ", ".join(parts)
    
    # 1. Browser Push
    if settings.get("notifications_browser"):
        try:
            result = await send_push_notification(
                title="DupeManager",
                message=f"{duplicates_found} duplicados nuevos detectados",
                url="/",
            )
            results["push"] = result
        except Exception as e:
            results["push"] = {"success": False, "error": str(e)}
    
    # 2. Webhook
    if settings.get("notifications_webhook_enabled"):
        url = settings.get("notifications_webhook_url")
        if url:
            try:
                result = await send_duplicate_notification(
                    url=url,
                    duplicates_found=duplicates_found,
                    details=details,
                )
                results["webhook"] = result
            except Exception as e:
                results["webhook"] = {"success": False, "error": str(e)}
    
    # 3. Email
    if settings.get("notifications_email_enabled"):
        try:
            result = await send_duplicate_email(
                smtp_host=settings.get("notifications_email_smtp_host"),
                smtp_port=settings.get("notifications_email_smtp_port"),
                username=settings.get("notifications_email_username"),
                password=settings.get("notifications_email_password"),
                to_email=settings.get("notifications_email_to"),
                duplicates_found=duplicates_found,
                details=details,
            )
            results["email"] = result
        except Exception as e:
            results["email"] = {"success": False, "error": str(e)}
    
    return {
        "success": True,
        "methods_notified": list(results.keys()),
        "results": results,
    }


async def send_test_notification(method: str) -> dict:
    """
    Envía una notificación de prueba.
    
    Args:
        method: "push", "webhook", o "email"
    """
    settings = await get_all_settings()
    
    if method == "push":
        result = await send_push_notification(
            title="DupeManager - Prueba",
            message="¡Las notificaciones push están funcionando!",
            url="/",
        )
        return result
    
    elif method == "webhook":
        url = settings.get("notifications_webhook_url")
        if not url:
            return {"success": False, "error": "URL del webhook no configurada"}
        
        result = await send_webhook(
            url=url,
            title="DupeManager - Prueba",
            message="¡El webhook está funcionando!",
            tags=["dupemanager", "test"],
        )
        return result
    
    elif method == "email":
        return await send_email(
            smtp_host=settings.get("notifications_email_smtp_host"),
            smtp_port=settings.get("notifications_email_smtp_port"),
            username=settings.get("notifications_email_username"),
            password=settings.get("notifications_email_password"),
            to_email=settings.get("notifications_email_to"),
            subject="DupeManager - Prueba de email",
            body="Este es un email de prueba de DupeManager.",
        )
    
    else:
        return {"success": False, "error": f"Método no válido: {method}"}
