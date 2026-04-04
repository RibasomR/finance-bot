"""
Конфигурация окружения Alembic для миграций базы данных.

Настраивает подключение к БД и автогенерацию миграций.
"""

from logging.config import fileConfig
import asyncio
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

from config import get_settings
from bot.models import Base

## Конфигурация Alembic
config = context.config

## Настройка логирования из alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

## Целевая метадата для автогенерации
target_metadata = Base.metadata


def get_url():
    """
    Получить URL базы данных из переменных окружения.
    
    Приоритет: сначала проверяет os.environ (Docker runtime),
    затем загружает из .env файла (локальная разработка).
    
    :return: URL подключения к PostgreSQL
    :raises ValueError: Если DATABASE_URL не задан
    """
    import os
    from dotenv import load_dotenv
    
    ## First check runtime environment variables (Docker Compose)
    database_url = os.environ.get("DATABASE_URL")
    
    ## If not found, try loading from .env file (local development)
    if not database_url:
        load_dotenv()
        database_url = os.getenv("DATABASE_URL")
    
    ## Fail fast if DATABASE_URL is not configured
    if not database_url:
        raise ValueError(
            "DATABASE_URL is not set. Please configure it in .env file "
            "or set as environment variable in Docker Compose."
        )
    
    return database_url


## Установка URL из настроек
config.set_main_option("sqlalchemy.url", get_url())


def run_migrations_offline() -> None:
    """
    Запуск миграций в 'offline' режиме.
    
    Генерирует SQL скрипты без фактического подключения к БД.
    Используется для создания SQL файлов миграций.
    
    :return: None
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """
    Выполнить миграции с использованием предоставленного подключения.
    
    :param connection: Подключение к базе данных
    :return: None
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    Запуск миграций в асинхронном режиме.
    
    Создает асинхронное подключение и выполняет миграции.
    
    :return: None
    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """
    Запуск миграций в 'online' режиме.
    
    Подключается к БД и выполняет миграции в асинхронном режиме.
    
    :return: None
    """
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

