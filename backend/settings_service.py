"""DupeManager — Servicio de Configuración"""

import json
from typing import Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import async_session, Settings
from backend.config import settings as default_settings


# Defaults desde .env
DEFAULTS = {
    "trash_enabled": True,
    "trash_retention_value": 30,
    "trash_retention_unit": "days",
    "auto_scan_enabled": True,
    "auto_scan_value": 1,
    "auto_scan_unit": "days",
    "notifications_browser": False,
    "notifications_webhook_enabled": False,
    "notifications_webhook_url": "",
    "notifications_email_enabled": False,
    "notifications_email_smtp_host": "",
    "notifications_email_smtp_port": 587,
    "notifications_email_username": "",
    "notifications_email_password": "",
    "notifications_email_to": "",
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
