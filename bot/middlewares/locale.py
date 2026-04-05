"""
Middleware для определения языка пользователя.

Извлекает язык из БД и передаёт в data["lang"] для использования в хендлерах.
"""

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Update, Message, CallbackQuery
from loguru import logger
from sqlalchemy import select

from bot.models import get_session, User


class LocaleMiddleware(BaseMiddleware):
    """
    Middleware для определения языка пользователя.

    Для каждого входящего события извлекает язык пользователя из БД
    и помещает его в data["lang"].

    Для неизвестных пользователей (нет в БД) используется "ru" по умолчанию.
    """

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        """
        Определить язык пользователя и передать в данные обработчика.

        :param handler: Следующий обработчик в цепочке
        :param event: Объект обновления от Telegram
        :param data: Дополнительные данные
        :return: Результат выполнения обработчика
        """
        # Извлекаем telegram_id из события
        telegram_id = None

        if isinstance(event, Message) and event.from_user:
            telegram_id = event.from_user.id
        elif isinstance(event, CallbackQuery) and event.from_user:
            telegram_id = event.from_user.id

        lang = "ru"  # fallback

        if telegram_id:
            try:
                async with get_session() as session:
                    result = await session.execute(
                        select(User.language).where(User.telegram_id == telegram_id)
                    )
                    user_lang = result.scalar_one_or_none()
                    if user_lang:
                        lang = user_lang
            except Exception:
                # При ошибке БД — молча используем fallback
                pass

        data["lang"] = lang
        return await handler(event, data)
