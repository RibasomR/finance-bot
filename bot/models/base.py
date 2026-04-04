"""
Базовые классы и настройки для моделей SQLAlchemy.

Содержит базовый класс для всех моделей и настройки подключения к БД.
"""

from datetime import datetime
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from sqlalchemy import MetaData, DateTime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func

from config import get_settings


## Соглашение по именованию для БД
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)


## Базовый класс для всех моделей
class Base(DeclarativeBase):
    """
    Базовый класс для всех моделей SQLAlchemy.
    
    Все модели наследуются от этого класса и автоматически получают
    общую метадату и настройки.
    """
    
    metadata = metadata
    
    __abstract__ = True


## Миксин для добавления временных меток
class TimestampMixin:
    """
    Миксин для автоматического добавления временных меток создания и обновления.
    
    :ivar created_at: Дата и время создания записи (timezone-aware UTC)
    :ivar updated_at: Дата и время последнего обновления записи (timezone-aware UTC)
    """
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Дата и время создания записи"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Дата и время последнего обновления"
    )


## Движок и сессия БД
engine = None
async_session_maker = None


def init_db() -> None:
    """
    Инициализация подключения к базе данных.
    
    Создает асинхронный движок и фабрику сессий для работы с PostgreSQL или SQLite.
    Должна быть вызвана один раз при запуске приложения.
    
    :return: None
    
    Example:
        >>> init_db()
        >>> async with get_session() as session:
        ...     result = await session.execute(select(User))
    """
    global engine, async_session_maker
    
    settings = get_settings()
    
    ## Определяем параметры в зависимости от типа БД
    engine_kwargs = {
        "echo": False,
    }
    
    ## Параметры пула только для PostgreSQL
    if "postgresql" in settings.database_url:
        engine_kwargs.update({
            "pool_size": 10,
            "max_overflow": 20,
            "pool_pre_ping": True,
            "pool_recycle": 3600
        })
    
    engine = create_async_engine(
        settings.database_url,
        **engine_kwargs
    )
    
    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )


async def create_tables() -> None:
    """
    Создание всех таблиц в базе данных.
    
    Выполняет создание всех таблиц согласно моделям SQLAlchemy.
    Должна быть вызвана после init_db().
    
    :return: None
    """
    if engine is None:
        raise Exception("Database not initialized. Call init_db() first.")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Получить асинхронную сессию БД.
    
    Генератор для использования в качестве context manager.
    Автоматически закрывает сессию после использования.
    
    :return: Асинхронная сессия SQLAlchemy
    :raises Exception: Если БД не была инициализирована
    
    Example:
        >>> async with get_session() as session:
        ...     user = await session.get(User, user_id)
    """
    if async_session_maker is None:
        raise Exception("Database not initialized. Call init_db() first.")
    
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def close_db() -> None:
    """
    Закрыть подключение к базе данных.
    
    Корректно завершает все соединения и освобождает ресурсы.
    Должна быть вызвана при остановке приложения.
    
    :return: None
    
    Example:
        >>> await close_db()
    """
    global engine
    
    if engine:
        await engine.dispose()

