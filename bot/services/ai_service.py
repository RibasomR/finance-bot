"""
Service for working with OpenAI-compatible AI APIs.

Provides transcription of voice messages via Whisper-compatible API
and parsing of transaction text via Chat Completions API.
Supports any OpenAI-compatible provider: Groq, OpenAI, Ollama, etc.
"""

import asyncio
import json
import random
import time
from typing import Optional, Dict, Any
from pathlib import Path
from decimal import Decimal, InvalidOperation

import httpx
from loguru import logger

from config import get_settings
from bot.utils.sanitizer import sanitize_url


## Default settings for parsing
DEFAULT_MAX_RETRIES = 3
DEFAULT_TIMEOUT = 10
DEFAULT_TOTAL_DEADLINE = 25
DEFAULT_MAX_TEXT_LENGTH = 1000


class AIServiceError(Exception):
    """
    Base exception for AI API errors.
    """
    pass


class TranscriptionError(AIServiceError):
    """
    Error during audio transcription.
    """
    pass


class ParsingError(AIServiceError):
    """
    Error during transaction text parsing.
    """
    pass


def _get_httpx_client_kwargs() -> dict:
    """
    Build kwargs for httpx.AsyncClient based on settings.

    Configures proxy if AI_PROXY is set.

    :return: Dictionary of kwargs for httpx.AsyncClient
    """
    settings = get_settings()
    kwargs: dict = {}

    proxy = settings.ai_proxy.strip() if settings.ai_proxy else ""
    if proxy:
        kwargs["proxies"] = proxy
        logger.debug(f"AI API proxy: {sanitize_url(proxy)}")

    return kwargs


## Transcribe audio to text via Whisper-compatible API
async def transcribe_audio(audio_path: str) -> str:
    """
    Transcribe audio file to text via Whisper-compatible API.

    Uses OpenAI-compatible /audio/transcriptions endpoint.
    Tries the configured whisper model first, falls back to whisper-large-v3 if unavailable.

    :param audio_path: Path to audio file (OGG format from Telegram)
    :return: Recognized text
    :raises TranscriptionError: If transcription fails
    :raises FileNotFoundError: If audio file not found

    Example:
        >>> text = await transcribe_audio("voice_message.ogg")
        >>> print(text)
        "Potratil 500 rublej na produkty"
    """
    if not Path(audio_path).exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    settings = get_settings()

    if not settings.ai_api_key:
        raise TranscriptionError(
            "AI API key not configured. "
            "Set AI_API_KEY in .env file."
        )

    logger.info(f"Starting transcription via Whisper API: {audio_path}")

    ## Check file size
    file_size = Path(audio_path).stat().st_size
    logger.info(f"Audio file size: {file_size} bytes ({file_size / 1024:.2f} KB)")

    ## Read audio file
    with open(audio_path, "rb") as f:
        audio_data = f.read()

    if len(audio_data) == 0:
        raise TranscriptionError("Empty audio file")

    ## Models to try: configured model first, then fallback
    models_to_try = [settings.ai_whisper_model]
    if settings.ai_whisper_model != "whisper-large-v3":
        models_to_try.append("whisper-large-v3")

    base_url = settings.ai_base_url.rstrip("/")
    client_kwargs = _get_httpx_client_kwargs()
    last_error = None

    async with httpx.AsyncClient(
        timeout=httpx.Timeout(60.0, connect=15.0),
        **client_kwargs
    ) as client:
        for model in models_to_try:
            logger.info(f"Trying model: {model}")
            try:
                response = await client.post(
                    f"{base_url}/audio/transcriptions",
                    headers={
                        "Authorization": f"Bearer {settings.ai_api_key}"
                    },
                    files={
                        "file": (Path(audio_path).name, audio_data, "audio/ogg")
                    },
                    data={
                        "model": model,
                        "language": "ru",
                        "response_format": "text"
                    },
                    timeout=30.0
                )

                if response.status_code == 200:
                    text = response.text.strip()
                    if text:
                        logger.success(f"Transcribed successfully ({model}): '{text[:100]}...'")
                        return text
                    else:
                        last_error = TranscriptionError("Empty transcription result")
                        continue

                elif response.status_code == 401:
                    raise TranscriptionError(
                        "Invalid AI API key (401 Unauthorized). "
                        "Check AI_API_KEY in .env file."
                    )

                elif response.status_code == 403:
                    logger.warning(f"Model {model} returned 403 Forbidden")
                    last_error = TranscriptionError(
                        f"Access denied (403 Forbidden) for model {model}. "
                        "The server IP may be blocked, or the API key lacks permissions. "
                        "Try setting AI_PROXY in .env if needed."
                    )
                    if model != models_to_try[-1]:
                        continue
                    raise last_error

                elif response.status_code == 429:
                    raise TranscriptionError(
                        "Rate limit exceeded (429). Try again later."
                    )

                else:
                    safe_response = response.text[:200]
                    logger.warning(f"Model {model} returned HTTP {response.status_code}: {safe_response}")
                    last_error = TranscriptionError(
                        f"AI API error: HTTP {response.status_code}"
                    )
                    if model != models_to_try[-1]:
                        continue

            except httpx.TimeoutException:
                logger.error(f"Timeout for model {model}")
                last_error = TranscriptionError("AI API timeout. Check connection and try again.")
                if model != models_to_try[-1]:
                    continue
            except TranscriptionError:
                raise
            except Exception as e:
                logger.error(f"Unexpected error for model {model}: {type(e).__name__}: {e}")
                last_error = TranscriptionError(f"Transcription failed: {e}")
                if model != models_to_try[-1]:
                    continue

    if last_error:
        raise last_error

    raise TranscriptionError("Transcription failed: all models unavailable")


## Calculate exponential backoff delay with jitter
def _calculate_backoff_delay(attempt: int, base_delay: float = 0.5, jitter_percent: float = 0.2) -> float:
    """
    Calculate exponential backoff delay with jitter.

    Uses formula: base_delay * (2 ^ attempt) +/- jitter_percent
    Example delays: 0.5s, 1s, 2s with +/-20% jitter

    :param attempt: Current attempt number (0-based)
    :param base_delay: Base delay in seconds
    :param jitter_percent: Jitter percentage (0.0-1.0)
    :return: Delay in seconds with jitter applied
    """
    exponential_delay = base_delay * (2 ** attempt)
    jitter = exponential_delay * jitter_percent * (2 * random.random() - 1)
    return exponential_delay + jitter


## Parse transaction text via Chat Completions API
async def parse_transaction_text(text: str) -> Optional[Dict[str, Any]]:
    """
    Parse transaction text via OpenAI-compatible Chat Completions API.

    Sends text to LLM to extract structured data:
    - Operation type (income/expense)
    - Amount (in rubles or dollars)
    - Currency (RUB/USD)
    - Category
    - Description

    Uses exponential backoff with jitter for retries and enforces total deadline.

    :param text: Text to parse (will be truncated to max_text_length)
    :return: Dictionary with recognized data or None on error
    :raises ParsingError: On critical parsing error

    Example:
        >>> data = await parse_transaction_text("Spent 500 rubles on groceries")
        >>> print(data)
        {
            "type": "expense",
            "amount": Decimal('500'),
            "currency": "RUB",
            "category": "Produkty",
            "description": None
        }
    """
    if not text or not text.strip():
        raise ParsingError("Empty text for parsing")

    settings = get_settings()

    ## Truncate text to maximum allowed length
    if len(text) > DEFAULT_MAX_TEXT_LENGTH:
        logger.warning(f"Text truncated from {len(text)} to {DEFAULT_MAX_TEXT_LENGTH} characters")
        text = text[:DEFAULT_MAX_TEXT_LENGTH]

    logger.info(f"Parsing transaction text via AI Chat API: '{text[:50]}...'")

    if not settings.ai_api_key:
        raise ParsingError(
            "AI API key not configured. "
            "Set AI_API_KEY in .env file."
        )

    ## Prompt for parsing transaction via LLM
    prompt = """Проанализируй текст и извлеки информацию о финансовой транзакции.
Верни JSON с полями:
- type: "income" или "expense"
- amount: число (только сумма, без валюты)
- currency: "RUB" или "USD" (валюта транзакции)
- category: строка (категория транзакции)
- description: строка или null (дополнительное описание)

Категории расходов: Продукты, Транспорт, Рестораны, Здоровье, Дом, Развлечения, Одежда, Другое
Категории доходов: Зарплата, Фриланс, Подарок, Инвестиции, Другое

Правила распознавания валюты:
- "рублей", "руб", "₽", "р" → RUB
- "долларов", "баксов", "долл", "$", "usd" → USD
- Если валюта не указана → RUB (по умолчанию)

Если чего-то нет - используй null.
Если "тысяч" или "тыс" - умножь сумму на 1000.

Текст: "{text}"

Верни ТОЛЬКО JSON, без дополнительного текста.""".format(text=text)

    base_url = settings.ai_base_url.rstrip("/")
    client_kwargs = _get_httpx_client_kwargs()

    ## Track total time spent for deadline enforcement
    start_time = time.monotonic()
    last_error = None

    for attempt in range(DEFAULT_MAX_RETRIES):
        ## Check if we exceeded total deadline
        elapsed = time.monotonic() - start_time
        if elapsed >= DEFAULT_TOTAL_DEADLINE:
            logger.error(f"Total deadline exceeded: {elapsed:.2f}s >= {DEFAULT_TOTAL_DEADLINE}s")
            raise ParsingError(
                f"AI API did not respond within {DEFAULT_TOTAL_DEADLINE}s. "
                "Try again later."
            )

        ## Calculate remaining time for this attempt
        remaining_time = DEFAULT_TOTAL_DEADLINE - elapsed
        attempt_timeout = min(DEFAULT_TIMEOUT, remaining_time)

        try:
            async with httpx.AsyncClient(
                timeout=attempt_timeout,
                **client_kwargs
            ) as client:
                response = await client.post(
                    f"{base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.ai_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": settings.ai_chat_model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.0,
                        "max_tokens": 500
                    }
                )

                if response.status_code != 200:
                    safe_response = response.text[:200]
                    logger.error(f"AI API error {response.status_code}: {safe_response}")

                    ## Handle authentication errors (401)
                    if response.status_code == 401:
                        raise ParsingError(
                            "Invalid AI API key. "
                            "Check AI_API_KEY in .env file."
                        )

                    last_error = ParsingError(f"AI API returned error: {response.status_code}")

                    if attempt < DEFAULT_MAX_RETRIES - 1:
                        delay = _calculate_backoff_delay(attempt)
                        logger.info(f"Retry in {delay:.2f}s (attempt {attempt + 1}/{DEFAULT_MAX_RETRIES})")
                        await asyncio.sleep(delay)
                        continue
                    raise last_error

                result = response.json()

                ## Check if response has choices
                if "choices" not in result or not result["choices"]:
                    logger.error(f"AI API returned unexpected response format: {result}")
                    last_error = ParsingError("AI API returned unexpected response format")
                    if attempt < DEFAULT_MAX_RETRIES - 1:
                        delay = _calculate_backoff_delay(attempt)
                        logger.info(f"Retry in {delay:.2f}s")
                        await asyncio.sleep(delay)
                        continue
                    raise last_error

                content = result["choices"][0]["message"]["content"].strip()

            ## Check if content is empty
            if not content:
                logger.error("AI API returned empty response")
                last_error = ParsingError("AI API returned empty response. Try again.")
                if attempt < DEFAULT_MAX_RETRIES - 1:
                    delay = _calculate_backoff_delay(attempt)
                    logger.info(f"Retry in {delay:.2f}s")
                    await asyncio.sleep(delay)
                    continue
                raise last_error

            ## Log raw content for debugging (first 200 chars)
            logger.debug(f"Raw response content: {content[:200]}...")

            ## Extract JSON from response (may be wrapped in ```json```)
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            ## Try to parse JSON
            try:
                transaction_data = json.loads(content)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from response. Content: {content[:500]}")
                logger.error(f"JSON decode error: {e}")
                last_error = ParsingError(
                    "Failed to process AI API response. "
                    "Response is not valid JSON. Try again."
                )
                if attempt < DEFAULT_MAX_RETRIES - 1:
                    delay = _calculate_backoff_delay(attempt)
                    logger.info(f"Retry in {delay:.2f}s")
                    await asyncio.sleep(delay)
                    continue
                raise last_error

            ## Validate data
            if not transaction_data.get("type") in ["income", "expense"]:
                raise ParsingError("Invalid transaction type")

            ## Convert amount to Decimal for precision
            try:
                amount = Decimal(str(transaction_data.get("amount", 0)))
            except (ValueError, InvalidOperation):
                raise ParsingError("Invalid amount format")

            if amount <= 0:
                raise ParsingError("Invalid transaction amount")

            if amount > 10_000_000:
                raise ParsingError("Amount too large (max 10,000,000)")

            ## Replace amount with Decimal
            transaction_data["amount"] = amount

            logger.success(f"Parsed successfully via AI Chat API: {transaction_data}")
            return transaction_data

        except httpx.TimeoutException:
            logger.warning(f"Timeout on AI API request (attempt {attempt + 1}/{DEFAULT_MAX_RETRIES})")
            last_error = ParsingError(
                "AI API unavailable (timeout). "
                "Check connection and try again later."
            )

            if attempt < DEFAULT_MAX_RETRIES - 1:
                delay = _calculate_backoff_delay(attempt)
                logger.info(f"Retry in {delay:.2f}s")
                await asyncio.sleep(delay)
                continue
            raise last_error

        except KeyError as e:
            from bot.utils.sanitizer import sanitize_exception_message
            safe_error = sanitize_exception_message(e)
            logger.error(f"Error accessing AI API response fields: {safe_error}")
            last_error = ParsingError(
                "Failed to process AI API response (unexpected format). "
                "Try again or contact administrator."
            )

            if attempt < DEFAULT_MAX_RETRIES - 1:
                delay = _calculate_backoff_delay(attempt)
                logger.info(f"Retry in {delay:.2f}s")
                await asyncio.sleep(delay)
                continue
            raise last_error

        except ParsingError:
            ## Re-raise parsing errors without retry
            raise

        except Exception as e:
            from bot.utils.sanitizer import sanitize_exception_message
            safe_error = sanitize_exception_message(e)
            logger.error(f"Unexpected error on AI API request: {safe_error}")
            last_error = ParsingError(f"AI API error: {safe_error}")

            if attempt < DEFAULT_MAX_RETRIES - 1:
                delay = _calculate_backoff_delay(attempt)
                logger.info(f"Retry in {delay:.2f}s")
                await asyncio.sleep(delay)
                continue
            raise last_error

    ## If we exhausted all retries, raise the last error
    if last_error:
        raise last_error

    raise ParsingError(
        "All AI API attempts failed. "
        "Try again later."
    )


## Find category by name with similarity matching
def find_matching_category(
    category_name: Optional[str],
    available_categories: list,
    default_category_name: str = "Другое"
) -> tuple[Optional[int], str]:
    """
    Find matching category by name from recognized text.

    Searches for category by partial name match (case-insensitive).
    If not found - returns default category.

    :param category_name: Category name from recognized text
    :param available_categories: List of available categories (Category objects)
    :param default_category_name: Default category name
    :return: Tuple (category_id, category_display_name)

    Example:
        >>> categories = [Category(id=1, name="Produkty"), Category(id=2, name="Drugoe")]
        >>> category_id, name = find_matching_category("prod", categories)
        >>> print(category_id, name)
        1 "Produkty"
    """
    if not category_name:
        ## Find default category
        for cat in available_categories:
            if cat.name == default_category_name:
                return cat.id, cat.name
        return None, default_category_name

    category_name_lower = category_name.lower().strip()

    ## Exact match
    for cat in available_categories:
        if cat.name.lower() == category_name_lower:
            return cat.id, cat.name

    ## Partial match
    for cat in available_categories:
        if category_name_lower in cat.name.lower() or cat.name.lower() in category_name_lower:
            return cat.id, cat.name

    ## Not found - return default
    for cat in available_categories:
        if cat.name == default_category_name:
            return cat.id, cat.name

    return None, default_category_name
