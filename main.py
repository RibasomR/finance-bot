"""
Главный модуль Telegram-бота для учета доходов и расходов.

Инициализирует бота, регистрирует handlers и запускает polling.
"""

import asyncio
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from loguru import logger

from config import get_settings
from bot.utils.logger import setup_logging
from bot.handlers import common, voice, transactions, view, categories, export, settings
from bot.models import init_db, create_tables, close_db
from bot.models import User, Category, Transaction  # Import models to register them in metadata
from bot.services.database import initialize_default_categories
from bot.middlewares import (
    RateLimitMiddleware,
    ErrorHandlerMiddleware,
    LocaleMiddleware,
)
from bot.utils.validators import (
    initialize_rate_limiter,
    InMemoryRateLimiterBackend,
    RedisRateLimiterBackend,
)


## Инициализация и запуск бота
async def main() -> None:
    """
    Главная функция запуска бота.
    
    Выполняет следующие действия:
    1. Настраивает систему логирования
    2. Загружает конфигурацию из переменных окружения
    3. Инициализирует подключение к базе данных
    4. Создает предустановленные категории
    5. Инициализирует Redis для rate limiting
    6. Создает экземпляры Bot и Dispatcher
    7. Регистрирует middlewares
    8. Регистрирует все handlers
    9. Запускает polling для получения обновлений
    
    :return: None
    :raises Exception: При критических ошибках инициализации или работы бота
    """
    setup_logging()
    logger.info("🚀 Запуск бота...")
    
    try:
        config_settings = get_settings()
        logger.info("✅ Конфигурация загружена успешно")
    except Exception as e:
        # Mask sensitive data in exception message
        from bot.utils.sanitizer import sanitize_exception_message
        safe_error = sanitize_exception_message(e)
        logger.critical(f"❌ Ошибка загрузки конфигурации: {safe_error}")
        sys.exit(1)
    
    try:
        init_db()
        logger.info("✅ База данных инициализирована")
    except Exception as e:
        from bot.utils.sanitizer import sanitize_exception_message
        safe_error = sanitize_exception_message(e)
        logger.critical(f"❌ Ошибка инициализации БД: {safe_error}")
        sys.exit(1)
    
    try:
        await create_tables()
        logger.info("✅ Таблицы БД созданы/проверены")
    except Exception as e:
        from bot.utils.sanitizer import sanitize_exception_message
        safe_error = sanitize_exception_message(e)
        logger.critical(f"❌ Ошибка создания таблиц БД: {safe_error}")
        sys.exit(1)
    
    try:
        await initialize_default_categories()
        logger.info("✅ Предустановленные категории проверены")
    except Exception as e:
        from bot.utils.sanitizer import sanitize_exception_message
        safe_error = sanitize_exception_message(e)
        logger.error(f"⚠️ Ошибка инициализации категорий: {safe_error}")
    
    ## Initialize rate limiter with Redis or fallback to in-memory
    redis_client = None
    try:
        import redis.asyncio as redis
        from bot.utils.sanitizer import sanitize_url
        
        # Sanitize Redis URL for logging
        safe_redis_url = sanitize_url(config_settings.redis_url)
        
        redis_client = redis.from_url(
            config_settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        # Test Redis connection
        await redis_client.ping()
        initialize_rate_limiter(RedisRateLimiterBackend(redis_client))
        logger.info(f"✅ Rate limiting активирован (Redis backend: {safe_redis_url})")
    except Exception as e:
        from bot.utils.sanitizer import sanitize_exception_message
        safe_error = sanitize_exception_message(e)
        logger.warning(f"⚠️ Redis недоступен: {safe_error}")
        logger.info("🔄 Переключение на in-memory rate limiting (dev fallback)")
        initialize_rate_limiter(InMemoryRateLimiterBackend())
        logger.info("✅ Rate limiting активирован (in-memory backend)")
    
    bot = Bot(
        token=config_settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    ## Устанавливаем меню команд бота на двух языках
    from bot.locales import t

    ru_commands = [
        BotCommand(command="menu", description=f"📋 {t('cmd_menu', 'ru')}"),
        BotCommand(command="add", description=f"➕ {t('cmd_add', 'ru')}"),
        BotCommand(command="stats", description=f"📊 {t('cmd_stats', 'ru')}"),
        BotCommand(command="help", description=f"❓ {t('cmd_help', 'ru')}"),
    ]
    en_commands = [
        BotCommand(command="menu", description=f"📋 {t('cmd_menu', 'en')}"),
        BotCommand(command="add", description=f"➕ {t('cmd_add', 'en')}"),
        BotCommand(command="stats", description=f"📊 {t('cmd_stats', 'en')}"),
        BotCommand(command="help", description=f"❓ {t('cmd_help', 'en')}"),
    ]
    await bot.set_my_commands(ru_commands, language_code="ru")
    await bot.set_my_commands(en_commands, language_code="en")
    await bot.set_my_commands(ru_commands)  # default
    logger.info("✅ Меню команд установлено (ru/en)")
    
    dp = Dispatcher()
    
    ## Регистрируем middlewares
    dp.message.middleware(RateLimitMiddleware(max_requests=20, time_window=60))
    dp.callback_query.middleware(RateLimitMiddleware(max_requests=20, time_window=60))

    dp.message.middleware(LocaleMiddleware())
    dp.callback_query.middleware(LocaleMiddleware())
    logger.info("✅ Locale middleware активирован")

    dp.message.middleware(ErrorHandlerMiddleware())
    dp.callback_query.middleware(ErrorHandlerMiddleware())
    logger.info("✅ Error handler активирован")
    
    dp.include_router(view.router)
    dp.include_router(settings.router)
    dp.include_router(categories.router)
    dp.include_router(export.router)
    dp.include_router(voice.router)
    dp.include_router(transactions.router)
    dp.include_router(common.router)
    logger.info("✅ Handlers зарегистрированы")
    
    try:
        logger.info("🔄 Начинаю polling...")
        logger.info("✅ Бот успешно запущен и готов к работе")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except KeyboardInterrupt:
        logger.info("⛔ Получен сигнал остановки (Ctrl+C)")
    except Exception as e:
        from bot.utils.sanitizer import sanitize_exception_message
        safe_error = sanitize_exception_message(e)
        logger.critical(f"❌ Критическая ошибка при работе бота: {safe_error}")
        raise
    finally:
        logger.info("🔄 Начинаю graceful shutdown...")
        await bot.session.close()
        await close_db()
        if redis_client:
            await redis_client.close()
            logger.info("✅ Redis соединение закрыто")
        logger.info("👋 Бот остановлен")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⛔ Получен сигнал остановки (Ctrl+C)")
    except Exception as e:
        from bot.utils.sanitizer import sanitize_exception_message
        safe_error = sanitize_exception_message(e)
        logger.critical(f"💥 Необработанная ошибка: {safe_error}")
        sys.exit(1)

