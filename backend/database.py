"""DupeManager — Database Models"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum, ForeignKey, Text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime, timezone
from typing import Optional
import enum

from backend.config import settings


class Base(DeclarativeBase):
    pass


class DuplicateStatus(str, enum.Enum):
    PENDING = "pending"
    RESOLVED = "resolved"
    IGNORED = "ignored"


class ActionType(str, enum.Enum):
    KEEP = "keep"
    IGNORE = "ignore"
    SKIP = "skip"


class ScanStatus(Base):
    """Estado del último escaneo"""
    __tablename__ = "scan_status"

    id = Column(Integer, primary_key=True, default=1)
    last_scan_at = Column(DateTime, nullable=True)
    running = Column(Boolean, default=False)
    progress = Column(Float, default=0.0)
    current_item = Column(String, nullable=True)
    total_items = Column(Integer, default=0)
    message = Column(String, nullable=True)


class EpisodeDuplicate(Base):
    """Grupo de episodios duplicados"""
    __tablename__ = "episode_duplicates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(String, unique=True, nullable=False, index=True)
    series_name = Column(String, nullable=False)
    normalized_series = Column(String, nullable=False, index=True)
    season = Column(Integer, nullable=False)
    episode = Column(Integer, nullable=False)
    status = Column(String, default=DuplicateStatus.PENDING)
    total_size = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    copies = relationship("EpisodeCopy", back_populates="duplicate_group", cascade="all, delete-orphan")


class EpisodeCopy(Base):
    """Copia individual de un episodio duplicado"""
    __tablename__ = "episode_copies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    duplicate_id = Column(Integer, ForeignKey("episode_duplicates.id"), nullable=False)
    jellyfin_item_id = Column(String, nullable=True)
    path = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    size = Column(Float, default=0.0)
    resolution = Column(String, nullable=True)
    codec = Column(String, nullable=True)
    quality_score = Column(Integer, default=-1)
    is_best = Column(Boolean, default=False)
    media_streams_json = Column(Text, nullable=True)

    duplicate_group = relationship("EpisodeDuplicate", back_populates="copies")


class MovieDuplicate(Base):
    """Grupo de películas duplicadas"""
    __tablename__ = "movie_duplicates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    normalized_name = Column(String, nullable=False, index=True)
    year = Column(Integer, nullable=True)
    status = Column(String, default=DuplicateStatus.PENDING)
    total_size = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    copies = relationship("MovieCopy", back_populates="duplicate_group", cascade="all, delete-orphan")


class MovieCopy(Base):
    """Copia individual de una película duplicada"""
    __tablename__ = "movie_copies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    duplicate_id = Column(Integer, ForeignKey("movie_duplicates.id"), nullable=False)
    jellyfin_item_id = Column(String, nullable=True)
    path = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    size = Column(Float, default=0.0)
    resolution = Column(String, nullable=True)
    codec = Column(String, nullable=True)
    quality_score = Column(Integer, default=-1)
    is_best = Column(Boolean, default=False)
    media_streams_json = Column(Text, nullable=True)

    duplicate_group = relationship("MovieDuplicate", back_populates="copies")


class IgnoredDuplicate(Base):
    """Duplicados ignorados por el usuario"""
    __tablename__ = "ignored_duplicates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    item_type = Column(String, nullable=False)  # "episode" or "movie"
    ignored_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Settings(Base):
    """Configuración persistente en BD"""
    __tablename__ = "settings"

    key = Column(String, primary_key=True)
    value = Column(Text, nullable=False)


# Database engine
engine = create_async_engine(settings.database_url, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    """Inicializa la base de datos"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    """Dependency para obtener sesión de BD"""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
