"""DupeManager — Webhook Notifications"""

import httpx
from typing import Optional


async def send_webhook(
    url: str,
    title: str,
    message: str,
    priority: str = "normal",
    tags: list[str] = None,
) -> dict:
    """
    Envía notificación vía webhook (HTTP POST).
    
    Compatible con:
    - ntfy.sh
    - Gotify
    - Discord
    - Telegram Bot
    - Slack
    """
    if not url:
        return {"success": False, "error": "URL no configurada"}
    
    payload = {
        "title": title,
        "message": message,
        "priority": priority,
        "tags": tags or ["dupemanager"],
    }
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
        
        return {
            "success": True,
            "status_code": response.status_code,
            "message": "Webhook enviado correctamente",
        }
    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "error": f"HTTP {e.response.status_code}: {e.response.text}",
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


async def send_duplicate_notification(
    url: str,
    duplicates_found: int,
    details: str = "",
) -> dict:
    """
    Envía notificación de nuevos duplicados detectados.
    """
    title = "DupeManager"
    message = f"Se detectaron {duplicates_found} duplicados nuevos"
    if details:
        message += f"\n{details}"
    
    return await send_webhook(
        url=url,
        title=title,
        message=message,
        priority="high",
        tags=["dupemanager", "duplicates", "warning"],
    )
