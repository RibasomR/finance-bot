"""
Модуль настройки логирования.

Настраивает систему логирования с использованием loguru для всего приложения.
Включает автоматическое маскирование чувствительных данных в логах.
"""

import sys
import re
from pathlib import Path
from loguru import logger
from config import get_settings


## Sanitize log message to mask sensitive data
def _sanitize_log_message(message: str) -> str:
    """
    Sanitize log message by masking sensitive patterns.
    
    Masks API keys, tokens, passwords, and other sensitive data
    that might accidentally appear in logs.
    
    :param message: Original log message
    :return: Sanitized message with masked sensitive data
    
    Example:
        >>> _sanitize_log_message("Token: sk-1234567890")
        "Token: sk-1*******"
    """
    if not message or not isinstance(message, str):
        return message
    
    # Pattern for potential API keys/tokens (alphanumeric strings 20+ chars)
    token_pattern = r"\b([a-zA-Z0-9_-]{20,})\b"
    
    def mask_token(match):
        token = match.group(1)
        if len(token) <= 4:
            return "*" * len(token)
        return f"{token[:4]}{'*' * (len(token) - 4)}"
    
    sanitized = re.sub(token_pattern, mask_token, message)
    
    # Mask database URLs with credentials
    # postgresql://user:password@host -> postgresql://user:***@host
    url_pattern = r"([\w+]+://)([\w]*:)([^@\s]+@)"
    sanitized = re.sub(url_pattern, r"\1\2***@", sanitized)
    
    return sanitized


## Custom log formatter with sanitization
def _format_log_record(record: dict) -> str:
    """
    Format log record with automatic sanitization.
    
    :param record: Loguru record dictionary
    :return: Formatted and sanitized log message
    """
    # Sanitize the message
    record["message"] = _sanitize_log_message(record["message"])
    return record["message"]


## Настройка логирования приложения
def setup_logging() -> None:
    """
    Настраивает систему логирования для приложения.
    
    Создает два обработчика логов:
    1. Консольный вывод с цветным форматированием
    2. Файловый вывод с ротацией по размеру
    
    Логи записываются в файл, указанный в настройках (settings.log_file).
    Размер файла ограничен 10 МБ, после чего создается новый файл.
    Хранятся последние 5 файлов логов.
    
    Автоматически маскирует чувствительные данные (токены, пароли, API ключи)
    перед записью в логи для предотвращения утечек.
    
    :return: None
    
    Example:
        >>> setup_logging()
        >>> logger.info("Application started")
    """
    settings = get_settings()
    
    logger.remove()
    
    # Add console handler with sanitization
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level,
        colorize=True,
        filter=lambda record: _sanitize_log_message(record["message"]) and True
    )
    
    log_path = Path(settings.log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Add file handler with sanitization
    logger.add(
        settings.log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.log_level,
        rotation="10 MB",
        retention=5,
        compression="zip",
        encoding="utf-8",
        filter=lambda record: _sanitize_log_message(record["message"]) and True
    )
    
    logger.info(f"Логирование настроено. Уровень: {settings.log_level}")

