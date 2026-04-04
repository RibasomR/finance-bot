"""
Utility module for sanitizing sensitive data in logs.

Provides functions to mask/redact sensitive information like API keys,
tokens, passwords before logging to prevent security leaks.
"""

import re
from typing import Any, Dict, Union


## Mask sensitive string value
def mask_sensitive_value(value: str, visible_chars: int = 4, mask_char: str = "*") -> str:
    """
    Mask sensitive string value, showing only first N characters.
    
    Replaces most of the string with mask characters, leaving only
    the first few characters visible for identification purposes.
    
    :param value: Original sensitive value
    :param visible_chars: Number of characters to keep visible at start
    :param mask_char: Character to use for masking
    :return: Masked string
    
    Example:
        >>> mask_sensitive_value("sk-1234567890abcdef")
        "sk-1***************"
        >>> mask_sensitive_value("my_secret_token", visible_chars=3)
        "my_************"
    """
    if not value or not isinstance(value, str):
        return "***"
    
    if len(value) <= visible_chars:
        return mask_char * len(value)
    
    visible_part = value[:visible_chars]
    masked_part = mask_char * (len(value) - visible_chars)
    return f"{visible_part}{masked_part}"


## Sanitize dictionary with sensitive keys
def sanitize_dict(
    data: Dict[str, Any],
    sensitive_keys: set = None,
    visible_chars: int = 4
) -> Dict[str, Any]:
    """
    Sanitize dictionary by masking values of sensitive keys.
    
    Recursively processes nested dictionaries and masks values
    for keys that contain sensitive information.
    
    :param data: Dictionary to sanitize
    :param sensitive_keys: Set of key names to mask (case-insensitive)
    :param visible_chars: Number of characters to keep visible
    :return: Sanitized dictionary copy
    
    Example:
        >>> data = {"api_key": "secret123", "username": "john"}
        >>> sanitize_dict(data)
        {"api_key": "secr*****", "username": "john"}
    """
    if sensitive_keys is None:
        sensitive_keys = {
            "token", "api_key", "apikey", "api-key",
            "password", "passwd", "pwd",
            "secret", "authorization", "auth",
            "bot_token", "ai_api_key",
            "database_url", "redis_url",
            "access_token", "refresh_token",
            "private_key", "secret_key"
        }
    
    if not isinstance(data, dict):
        return data
    
    sanitized = {}
    for key, value in data.items():
        key_lower = key.lower().replace("_", "").replace("-", "")
        
        # Check if key contains sensitive information
        is_sensitive = any(sensitive in key_lower for sensitive in sensitive_keys)
        
        if is_sensitive and isinstance(value, str):
            sanitized[key] = mask_sensitive_value(value, visible_chars)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict(value, sensitive_keys, visible_chars)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_dict(item, sensitive_keys, visible_chars) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            sanitized[key] = value
    
    return sanitized


## Sanitize URL by masking credentials
def sanitize_url(url: str) -> str:
    """
    Sanitize URL by masking embedded credentials.
    
    Masks username and password in URLs like:
    postgresql://user:password@host:port/db -> postgresql://user:***@host:port/db
    redis://user:password@host:port -> redis://user:***@host:port
    
    :param url: URL string that may contain credentials
    :return: Sanitized URL with masked credentials
    
    Example:
        >>> sanitize_url("postgresql://admin:secret123@localhost:5432/mydb")
        "postgresql://admin:***@localhost:5432/mydb"
        >>> sanitize_url("redis://:password@localhost:6379/0")
        "redis://:***@localhost:6379/0"
    """
    if not url or not isinstance(url, str):
        return "***"
    
    # Pattern to match URLs with credentials
    # Matches: scheme://[user[:password]@]host[:port][/path]
    pattern = r"([\w+]+://)([\w]*:)([^@]+@)"
    
    def mask_credentials(match):
        scheme = match.group(1)  # scheme://
        user = match.group(2)    # user: or empty
        password_at = match.group(3)  # password@ or @
        
        # Mask password part
        return f"{scheme}{user}***@"
    
    sanitized = re.sub(pattern, mask_credentials, url)
    return sanitized


## Sanitize HTTP headers
def sanitize_headers(headers: Dict[str, str]) -> Dict[str, str]:
    """
    Sanitize HTTP headers by masking authorization tokens.
    
    Masks values in headers like Authorization, X-API-Key, etc.
    
    :param headers: Dictionary of HTTP headers
    :return: Sanitized headers dictionary
    
    Example:
        >>> headers = {"Authorization": "Bearer sk-123456", "Content-Type": "application/json"}
        >>> sanitize_headers(headers)
        {"Authorization": "Bear**********", "Content-Type": "application/json"}
    """
    sensitive_header_names = {
        "authorization", "x-api-key", "api-key",
        "x-auth-token", "x-access-token"
    }
    
    sanitized = {}
    for key, value in headers.items():
        if key.lower() in sensitive_header_names:
            sanitized[key] = mask_sensitive_value(value, visible_chars=4)
        else:
            sanitized[key] = value
    
    return sanitized


## Sanitize exception message
def sanitize_exception_message(exception: Exception) -> str:
    """
    Sanitize exception message by masking potential sensitive data.
    
    Scans exception message for patterns that look like tokens/keys
    and masks them before logging.
    
    :param exception: Exception object
    :return: Sanitized exception message
    
    Example:
        >>> exc = ValueError("Invalid token: sk-1234567890abcdef")
        >>> sanitize_exception_message(exc)
        "Invalid token: sk-1***************"
    """
    message = str(exception)
    
    # Pattern for potential API keys/tokens (alphanumeric strings with dashes/underscores, 16+ chars)
    token_pattern = r"\b([a-zA-Z0-9_-]{16,})\b"
    
    def mask_token(match):
        token = match.group(1)
        # Only mask if it looks like a token (has mix of chars or starts with known prefixes)
        if len(token) >= 16:
            return mask_sensitive_value(token, visible_chars=4)
        return token
    
    sanitized = re.sub(token_pattern, mask_token, message)
    
    # Also mask database URLs with credentials
    url_pattern = r"([\w+]+://)([\w]*:)([^@\s]+@)"
    sanitized = re.sub(url_pattern, r"\1\2***@", sanitized)
    
    return sanitized


## Sanitize text for logging
def sanitize_for_logging(text: str) -> str:
    """
    Sanitize arbitrary text by masking potential sensitive patterns.
    
    Useful for sanitizing user input or API responses before logging.
    Looks for patterns like tokens, keys, passwords in text.
    
    :param text: Text to sanitize
    :return: Sanitized text
    
    Example:
        >>> sanitize_for_logging("API key is sk-1234567890abcdef")
        "API key is sk-1***************"
    """
    if not text or not isinstance(text, str):
        return str(text)
    
    # Pattern for potential secrets (long alphanumeric strings)
    secret_pattern = r"\b([a-zA-Z0-9_-]{32,})\b"
    
    def mask_secret(match):
        secret = match.group(1)
        return mask_sensitive_value(secret, visible_chars=6)
    
    sanitized = re.sub(secret_pattern, mask_secret, text)
    return sanitized

