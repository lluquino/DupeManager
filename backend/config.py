"""DupeManager — Configuración"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configuración del servicio leída de .env"""

    # Jellyfin
    jellyfin_url: str = "http://192.168.0.22:8096"
    jellyfin_api_key: str = ""

    # JWT
    jwt_secret: str = "change-me-to-a-random-secret"
    jwt_expiry_hours: int = 24

    # Media paths
    media_path: str = "/media"
    trash_path: str = "/media/tmp/DupeManager-trash"

    # Server
    host: str = "0.0.0.0"
    port: int = 8097

    # Database
    database_url: str = "sqlite+aiosqlite:///data/dupeManager.db"

    # Trash
    trash_enabled: bool = True
    trash_retention_value: int = 30
    trash_retention_unit: str = "days"

    # Auto scan
    auto_scan_enabled: bool = True
    auto_scan_value: int = 7
    auto_scan_unit: str = "days"

    # Notifications
    notifications_browser: bool = False
    notifications_webhook_enabled: bool = False
    notifications_webhook_url: str = ""
    notifications_email_enabled: bool = False
    notifications_email_smtp_host: str = ""
    notifications_email_smtp_port: int = 587
    notifications_email_username: str = ""
    notifications_email_password: str = ""
    notifications_email_to: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
