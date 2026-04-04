"""
Модуль конфигурации приложения.

Загружает переменные окружения и предоставляет настройки для всего приложения.
"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


## Класс настроек приложения
class Settings(BaseSettings):
    """
    Класс для управления настройками приложения.
    
    Загружает все необходимые переменные окружения и валидирует их.
    Использует pydantic-settings для автоматической загрузки из .env файла.
    
    :ivar bot_token: Токен Telegram бота
    :ivar database_url: URL для подключения к PostgreSQL
    :ivar redis_url: URL для подключения к Redis
    :ivar log_level: Уровень логирования
    :ivar log_file: Путь к файлу логов
    :ivar max_transaction_amount: Максимальная сумма транзакции
    :ivar rate_limit_requests: Количество запросов в период
    :ivar rate_limit_period: Период для rate limit в секундах
    :ivar ai_base_url: Base URL для OpenAI-совместимого API
    :ivar ai_api_key: API ключ для AI провайдера
    :ivar ai_chat_model: Модель для парсинга текста
    :ivar ai_whisper_model: Модель для транскрипции
    :ivar ai_proxy: HTTP прокси для AI API
    """
    
    bot_token: str = Field(..., validation_alias="BOT_TOKEN", description="Токен Telegram бота")
    database_url: str = Field(..., validation_alias="DATABASE_URL", description="URL базы данных PostgreSQL")
    redis_url: str = Field(default="redis://localhost:6379/0", validation_alias="REDIS_URL", description="URL Redis")
    
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL", description="Уровень логирования")
    log_file: str = Field(default="logs/bot.log", validation_alias="LOG_FILE", description="Путь к файлу логов")
    
    max_transaction_amount: int = Field(default=1000000, validation_alias="MAX_TRANSACTION_AMOUNT", description="Максимальная сумма транзакции")
    rate_limit_requests: int = Field(default=30, validation_alias="RATE_LIMIT_REQUESTS", description="Количество запросов в период")
    rate_limit_period: int = Field(default=60, validation_alias="RATE_LIMIT_PERIOD", description="Период rate limit в секундах")
    
    ## AI Provider (any OpenAI-compatible API)
    ai_base_url: str = Field(default="https://api.groq.com/openai/v1", validation_alias="AI_BASE_URL", description="Base URL для OpenAI-совместимого API")
    ai_api_key: str = Field(default="", validation_alias="AI_API_KEY", description="API ключ AI провайдера")
    ai_chat_model: str = Field(default="llama-3.3-70b-versatile", validation_alias="AI_CHAT_MODEL", description="Модель для парсинга транзакций")
    ai_whisper_model: str = Field(default="whisper-large-v3-turbo", validation_alias="AI_WHISPER_MODEL", description="Модель для транскрипции аудио")
    ai_proxy: str = Field(default="", validation_alias="AI_PROXY", description="HTTP прокси для AI API (опционально)")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """
        Валидация уровня логирования.
        
        :param v: Значение уровня логирования
        :return: Валидированный уровень в верхнем регистре
        :raises ValueError: Если уровень логирования некорректен
        """
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in allowed_levels:
            raise ValueError(f"Log level must be one of {allowed_levels}")
        return v_upper
    
    @field_validator("max_transaction_amount")
    @classmethod
    def validate_max_amount(cls, v: int) -> int:
        """
        Валидация максимальной суммы транзакции.
        
        :param v: Значение максимальной суммы
        :return: Валидированная сумма
        :raises ValueError: Если сумма меньше или равна нулю
        """
        if v <= 0:
            raise ValueError("Max transaction amount must be positive")
        return v


## Глобальный экземпляр настроек
settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Получить экземпляр настроек приложения.
    
    Создает новый экземпляр при первом вызове, затем возвращает существующий.
    Используется паттерн Singleton для единого экземпляра настроек.
    
    :return: Экземпляр класса Settings с загруженными настройками
    
    Example:
        >>> settings = get_settings()
        >>> print(settings.bot_token)
    """
    global settings
    if settings is None:
        settings = Settings()
    return settings

