"""DupeManager — Servicio de Configuración"""

import json
from typing import Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import async_session, Settings
from backend.config import settings as default_settings


# Defaults desde .env
DEFAULTS = {
    "trash_enabled": default_settings.trash_enabled,
    "trash_retention_value": default_settings.trash_retention_value,
    "trash_retention_unit": default_settings.trash_retention_unit,
    "auto_scan_enabled": default_settings.auto_scan_enabled,
    "auto_scan_value": default_settings.auto_scan_value,
    "auto_scan_unit": default_settings.auto_scan_unit,
    "notifications_browser": default_settings.notifications_browser,
    "notifications_webhook_enabled": default_settings.notifications_webhook_enabled,
    "notifications_webhook_url": default_settings.notifications_webhook_url,
    "notifications_email_enabled": default_settings.notifications_email_enabled,
    "notifications_email_smtp_host": default_settings.notifications_email_smtp_host,
    "notifications_email_smtp_port": default_settings.notifications_email_smtp_port,
    "notifications_email_username": default_settings.notifications_email_username,
    "notifications_email_password": default_settings.notifications_email_password,
    "notifications_email_to": default_settings.notifications_email_to,
}


async def get_setting(key: str) -> Any:
    """Obtiene un valor de configuración desde la BD"""
    async with async_session() as session:
        query = select(Settings).where(Settings.key == key)
        result = await session.execute(query)
        setting = result.scalar_one_or_none()
        
        if setting:
            try:
                return json.loads(setting.value)
            except (json.JSONDecodeError, TypeError):
                return setting.value
        
        return DEFAULTS.get(key)


async def get_all_settings() -> dict:
    """Obtiene todas las configuraciones"""
    result = {}
    
    async with async_session() as session:
        query = select(Settings)
        db_result = await session.execute(query)
        settings_list = db_result.scalars().all()
        
        # Cargar de BD
        db_settings = {}
        for s in settings_list:
            try:
                db_settings[s.key] = json.loads(s.value)
            except (json.JSONDecodeError, TypeError):
                db_settings[s.key] = s.value
        
        # Combinar con defaults
        for key, default in DEFAULTS.items():
            result[key] = db_settings.get(key, default)
    
    return result


async def update_settings(settings_dict: dict) -> bool:
    """Actualiza múltiples configuraciones"""
    async with async_session() as session:
        for key, value in settings_dict.items():
            if key in DEFAULTS:
                query = select(Settings).where(Settings.key == key)
                result = await session.execute(query)
                setting = result.scalar_one_or_none()
                
                if setting:
                    setting.value = json.dumps(value)
                else:
                    new_setting = Settings(key=key, value=json.dumps(value))
                    session.add(new_setting)
        
        await session.commit()
    
    return True


async def get_setting_value(key: str) -> Any:
    """Obtiene el valor de configuración (para uso interno)"""
    value = await get_setting(key)
    return value
