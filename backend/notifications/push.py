"""DupeManager — Browser Push Notifications"""

import json
from typing import Optional


# Almacén de suscripciones push (en producción usar BD)
_push_subscriptions: list[dict] = []


async def subscribe_push(subscription: dict) -> bool:
    """
    Registra una suscripción push del navegador.
    
    subscription contiene:
        - endpoint: URL del servicio push
        - keys: p256dh y auth keys
    """
    if subscription not in _push_subscriptions:
        _push_subscriptions.append(subscription)
    return True


async def unsubscribe_push(endpoint: str) -> bool:
    """Elimina una suscripción push"""
    global _push_subscriptions
    _push_subscriptions = [
        s for s in _push_subscriptions
        if s.get("endpoint") != endpoint
    ]
    return True


async def send_push_notification(title: str, message: str, url: str = "/") -> dict:
    """
    Envía notificación push a todos los suscriptores.
    
    Nota: Para envío real se necesita pywebpush o similar.
    Esta función prepara el payload para envío.
    """
    if not _push_subscriptions:
        return {"sent": 0, "message": "No hay suscriptores"}
    
    payload = {
        "title": title,
        "body": message,
        "icon": "/assets/logo.svg",
        "badge": "/assets/logo.svg",
        "url": url,
        "data": {
            "url": url,
        },
    }
    
    # En producción, aquí se usaría pywebpush:
    # from pywebpush import webpush
    # for sub in _push_subscriptions:
    #     try:
    #         webpush(sub, json.dumps(payload), vapid_private_key=...)
    #     except Exception:
    #         pass
    
    return {
        "sent": len(_push_subscriptions),
        "payload": payload,
        "message": f"Notificación preparada para {len(_push_subscriptions)} suscriptores",
    }


def get_subscription_count() -> int:
    """Retorna el número de suscriptores activos"""
    return len(_push_subscriptions)
