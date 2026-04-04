"""
Middlewares для бота.

Содержит промежуточные обработчики для различных задач.
"""

from .rate_limit import RateLimitMiddleware, StrictRateLimitMiddleware
from .error_handler import ErrorHandlerMiddleware, database_fallback_message, api_fallback_message

__all__ = [
    "RateLimitMiddleware",
    "StrictRateLimitMiddleware",
    "ErrorHandlerMiddleware",
    "database_fallback_message",
    "api_fallback_message",
]
