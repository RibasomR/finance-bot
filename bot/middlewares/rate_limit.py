"""
Middleware для ограничения частоты запросов (rate limiting).

Защищает бота от спама и перегрузки, ограничивая количество запросов
от пользователя в заданный период времени.
"""

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from loguru import logger

from bot.utils.validators import rate_limiter


## Middleware для rate limiting
class RateLimitMiddleware(BaseMiddleware):
    """
    Middleware для ограничения частоты запросов.
    
    Проверяет количество запросов от пользователя и блокирует
    при превышении лимита.
    
    :ivar max_requests: Максимальное количество запросов
    :ivar time_window: Временное окно в секундах
    """
    
    def __init__(self, max_requests: int = 20, time_window: int = 60):
        """
        Инициализация middleware.
        
        :param max_requests: Максимальное количество запросов в окне
        :param time_window: Временное окно в секундах
        
        Example:
            >>> middleware = RateLimitMiddleware(max_requests=10, time_window=60)
        """
        super().__init__()
        self.max_requests = max_requests
        self.time_window = time_window
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """
        Обработка события с проверкой rate limit.
        
        :param handler: Следующий обработчик в цепочке
        :param event: Событие Telegram (Message или CallbackQuery)
        :param data: Дополнительные данные
        :return: Результат обработки или None при превышении лимита
        """
        user_id = None
        
        # Получаем ID пользователя из события
        if isinstance(event, Message):
            user_id = event.from_user.id if event.from_user else None
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id if event.from_user else None
        
        if not user_id:
            # Если не удалось получить ID, пропускаем проверку
            return await handler(event, data)
        
        # Проверяем rate limit
        if rate_limiter is None:
            # Если rate limiter не инициализирован, пропускаем проверку
            return await handler(event, data)
        
        allowed, error_message = await rate_limiter.check_rate_limit(
            user_id=user_id,
            max_requests=self.max_requests,
            time_window=self.time_window
        )
        
        if not allowed:
            logger.warning(f"Rate limit exceeded for user {user_id}")
            
            # Отправляем сообщение о превышении лимита
            if isinstance(event, Message):
                await event.answer(
                    f"{error_message}\n\n"
                    "Пожалуйста, подождите перед следующим запросом.",
                    parse_mode="HTML"
                )
            elif isinstance(event, CallbackQuery):
                await event.answer(
                    "⏱ Слишком много запросов. Подождите немного.",
                    show_alert=True
                )
            
            return None
        
        # Продолжаем обработку
        return await handler(event, data)


## Специальный middleware для критичных операций (более строгий лимит)
class StrictRateLimitMiddleware(BaseMiddleware):
    """
    Строгий middleware для критичных операций.
    
    Используется для операций, требующих дополнительной защиты
    (например, создание транзакций, экспорт данных).
    """
    
    def __init__(self, max_requests: int = 5, time_window: int = 60):
        """
        Инициализация middleware.
        
        :param max_requests: Максимальное количество запросов
        :param time_window: Временное окно в секундах
        """
        super().__init__()
        self.max_requests = max_requests
        self.time_window = time_window
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """
        Обработка события с строгой проверкой rate limit.
        
        :param handler: Следующий обработчик в цепочке
        :param event: Событие Telegram
        :param data: Дополнительные данные
        :return: Результат обработки или None при превышении лимита
        """
        user_id = None
        
        if isinstance(event, Message):
            user_id = event.from_user.id if event.from_user else None
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id if event.from_user else None
        
        if not user_id:
            return await handler(event, data)
        
        # Проверяем rate limit с префиксом для разделения лимитов
        if rate_limiter is None:
            # Если rate limiter не инициализирован, пропускаем проверку
            return await handler(event, data)
        
        allowed, error_message = await rate_limiter.check_rate_limit(
            user_id=user_id * 1000,  # Используем другой namespace
            max_requests=self.max_requests,
            time_window=self.time_window
        )
        
        if not allowed:
            logger.warning(f"Strict rate limit exceeded for user {user_id}")
            
            if isinstance(event, Message):
                await event.answer(
                    "⏱ <b>Слишком частые операции</b>\n\n"
                    f"Ты превысил лимит запросов ({self.max_requests} за {self.time_window} сек).\n"
                    "Подожди немного перед следующей операцией.",
                    parse_mode="HTML"
                )
            elif isinstance(event, CallbackQuery):
                await event.answer(
                    "⏱ Превышен лимит операций. Подождите.",
                    show_alert=True
                )
            
            return None
        
        return await handler(event, data)
