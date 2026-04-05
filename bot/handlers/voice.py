"""
Обработчики для работы с голосовыми сообщениями.

Поддержка мультиязычности через locales.
"""

import os
from pathlib import Path
from typing import Optional

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, Voice
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from loguru import logger

from config import get_settings
from bot.states import VoiceTransactionStates
from bot.keyboards.voice_keyboards import (
    get_voice_confirmation_keyboard,
    get_voice_edit_keyboard,
    get_voice_categories_keyboard,
    get_voice_edit_cancel_keyboard,
)
from bot.keyboards.view_keyboards import get_edit_transaction_button
from bot.services.database import (
    get_or_create_user,
    get_categories,
    create_transaction,
)
from bot.services.ai_service import (
    transcribe_audio,
    parse_transaction_text,
    find_matching_category,
    TranscriptionError,
    ParsingError,
)
from bot.models import CategoryType, TransactionType
from bot.locales import t, translate_category_name


router = Router(name="voice")


## Обработка голосового сообщения
@router.message(F.voice)
async def handle_voice_message(message: Message, state: FSMContext, lang: str = "ru") -> None:
    """Voice message handler."""
    user = await get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )

    processing_msg = await message.answer(f"\U0001f3a4 {t('voice_processing', lang)}")

    voice: Voice = message.voice
    audio_path = None

    try:
        file = await message.bot.get_file(voice.file_id)

        temp_dir = Path("temp_audio")
        temp_dir.mkdir(exist_ok=True)

        audio_path = temp_dir / f"{message.from_user.id}_{voice.file_unique_id}.ogg"

        await message.bot.download_file(file.file_path, audio_path)

        file_size = audio_path.stat().st_size
        logger.info(f"Голосовое сообщение сохранено: {audio_path} (размер: {file_size} байт)")

        if file_size == 0:
            logger.error(f"Файл пустой! file_id={voice.file_id}")
            await processing_msg.edit_text(f"\u274c {t('voice_error_empty_file', lang)}")
            return

        with open(audio_path, "rb") as f:
            header = f.read(4)
            if header != b'OggS':
                logger.warning(f"Файл не является валидным OGG! Заголовок: {header}")

        await processing_msg.edit_text(f"\U0001f3a7 {t('voice_recognizing', lang)}")

        # Используем язык пользователя для Whisper
        whisper_lang = t("ai_whisper_language", lang)
        text = await transcribe_audio(str(audio_path), language=whisper_lang)
        logger.info(f"Текст распознан: {text}")

        await processing_msg.edit_text(f"\U0001f914 {t('voice_analyzing', lang)}")
        transaction_data = await parse_transaction_text(text, lang=lang)

        if not transaction_data:
            await processing_msg.edit_text(f"\u274c {t('voice_error_recognize', lang)}")
            return

        transaction_type = transaction_data["type"]
        category_type = CategoryType.EXPENSE if transaction_type == "expense" else CategoryType.INCOME

        categories = await get_categories(
            user_id=user.id,
            category_type=category_type,
            include_default=True
        )

        default_cat_name = t("cat_other", lang)
        category_id, category_name = find_matching_category(
            transaction_data.get("category"),
            categories,
            default_category_name=default_cat_name,
            lang=lang
        )

        if not category_id:
            await processing_msg.edit_text(f"\u274c {t('voice_error_category', lang)}")
            return

        category = next((c for c in categories if c.id == category_id), None)

        default_currency = t("ai_default_currency", lang)

        await state.update_data(
            user_id=user.id,
            transaction_type=transaction_type,
            amount=transaction_data["amount"],
            currency=transaction_data.get("currency", default_currency),
            category_id=category_id,
            category_name=category.name,
            category_emoji=category.emoji,
            description=transaction_data.get("description"),
            recognized_text=text,
            lang=lang
        )

        await state.set_state(VoiceTransactionStates.waiting_confirmation)

        await show_voice_confirmation(processing_msg, state, edit=True, lang=lang)

    except TranscriptionError as e:
        from bot.utils.sanitizer import sanitize_exception_message
        safe_error = sanitize_exception_message(e)
        logger.error(f"Ошибка транскрипции: {safe_error}")
        await processing_msg.edit_text(f"\u274c {t('voice_error_transcription', lang, error=str(e))}")
    except ParsingError as e:
        from bot.utils.sanitizer import sanitize_exception_message
        safe_error = sanitize_exception_message(e)
        logger.error(f"Ошибка парсинга: {safe_error}")
        await processing_msg.edit_text(f"\u274c {t('voice_error_parsing', lang, error=str(e))}")
    except Exception as e:
        from bot.utils.sanitizer import sanitize_exception_message
        safe_error = sanitize_exception_message(e)
        logger.error(f"Неожиданная ошибка при обработке голоса: {safe_error}")
        await processing_msg.edit_text(f"\u274c {t('voice_error_generic', lang)}")
    finally:
        if audio_path and audio_path.exists():
            try:
                os.remove(audio_path)
            except Exception as e:
                logger.warning(f"Не удалось удалить временный файл: {e}")


## Показ подтверждения
async def show_voice_confirmation(message: Message, state: FSMContext, edit: bool = False, lang: str = "ru") -> None:
    """Показать подтверждение голосовой транзакции."""
    data = await state.get_data()
    lang = data.get("lang", lang)

    transaction_type = data["transaction_type"]
    amount = data["amount"]
    currency = data.get("currency", "RUB")
    category_name = data["category_name"]
    category_emoji = data["category_emoji"]
    description = data.get("description")
    recognized_text = data.get("recognized_text", "")

    type_emoji = "\U0001f4b0" if transaction_type == "income" else "\U0001f4b8"
    type_text = t("tx_type_income", lang) if transaction_type == "income" else t("tx_type_expense", lang)
    sign = "+" if transaction_type == "income" else "-"
    currency_symbol = "\u20bd" if currency == "RUB" else "$"
    cat_display = translate_category_name(category_name, lang)

    text = (
        f"\U0001f3a4 <b>{t('voice_recognized_title', lang)}</b>\n\n"
        f"<i>\u00ab{recognized_text}\u00bb</i>\n\n"
        f"\U0001f4cb <b>{t('voice_transaction_data', lang)}</b>\n"
        f"{type_emoji} <b>{type_text}</b>\n"
        f"\U0001f4b5 {t('tx_amount_label', lang)}: <b>{sign}{float(amount):.2f} {currency_symbol}</b>\n"
        f"{category_emoji} {t('tx_category_label', lang)}: <b>{cat_display}</b>"
    )

    if description:
        text += f"\n\U0001f4dd {t('tx_description_label', lang)}: {description}"

    text += f"\n\n<i>{t('tx_confirm_correct', lang)}</i>"

    if edit:
        await message.edit_text(text, reply_markup=get_voice_confirmation_keyboard(lang))
    else:
        await message.answer(text, reply_markup=get_voice_confirmation_keyboard(lang))


## Подтверждение
@router.callback_query(StateFilter(VoiceTransactionStates.waiting_confirmation), F.data == "voice:confirm")
async def process_voice_confirm(callback: CallbackQuery, state: FSMContext, lang: str = "ru") -> None:
    """Подтвердить голосовую транзакцию."""
    data = await state.get_data()
    lang = data.get("lang", lang)

    try:
        transaction_type_str = data["transaction_type"]
        transaction_type = TransactionType.INCOME if transaction_type_str == "income" else TransactionType.EXPENSE

        transaction = await create_transaction(
            user_id=data["user_id"],
            transaction_type=transaction_type,
            amount=data["amount"],
            category_id=data["category_id"],
            description=data.get("description"),
            currency=data.get("currency", "RUB")
        )

        type_emoji = "\U0001f4b0" if transaction_type == TransactionType.INCOME else "\U0001f4b8"
        sign = "+" if transaction_type == TransactionType.INCOME else "-"
        currency_symbol = "\u20bd" if data.get("currency", "RUB") == "RUB" else "$"
        cat_display = translate_category_name(data['category_name'], lang)

        await callback.message.edit_text(
            f"\u2705 <b>{t('tx_saved', lang)}</b>\n\n"
            f"{type_emoji} {sign}{float(data['amount']):.2f} {currency_symbol}\n"
            f"{data['category_emoji']} {cat_display}",
            reply_markup=get_edit_transaction_button(transaction.id, lang)
        )

        await state.clear()

    except Exception as e:
        from bot.utils.sanitizer import sanitize_exception_message
        safe_error = sanitize_exception_message(e)
        logger.error(f"Ошибка сохранения голосовой транзакции: {safe_error}")
        await callback.message.edit_text(f"\u274c {t('tx_error_save', lang)}")
        await state.clear()

    await callback.answer()


## Переход к редактированию
@router.callback_query(StateFilter(VoiceTransactionStates.waiting_confirmation), F.data == "voice:edit")
async def process_voice_edit(callback: CallbackQuery, state: FSMContext, lang: str = "ru") -> None:
    """Перейти к редактированию."""
    data = await state.get_data()
    lang = data.get("lang", lang)

    type_emoji = "\U0001f4b0" if data["transaction_type"] == "income" else "\U0001f4b8"
    type_text = t("tx_type_income", lang) if data["transaction_type"] == "income" else t("tx_type_expense", lang)
    sign = "+" if data["transaction_type"] == "income" else "-"
    currency_symbol = "\u20bd" if data.get("currency", "RUB") == "RUB" else "$"
    cat_display = translate_category_name(data['category_name'], lang)

    text = (
        f"\u270f\ufe0f <b>{t('voice_edit_title', lang)}</b>\n\n"
        f"{type_emoji} <b>{type_text}</b>\n"
        f"\U0001f4b5 {t('tx_amount_label', lang)}: <b>{sign}{float(data['amount']):.2f} {currency_symbol}</b>\n"
        f"{data['category_emoji']} {t('tx_category_label', lang)}: <b>{cat_display}</b>\n"
    )

    if data.get("description"):
        text += f"\U0001f4dd {t('tx_description_label', lang)}: {data['description']}\n"

    text += f"\n<i>{t('voice_edit_choose_field', lang)}</i>"

    await callback.message.edit_text(text, reply_markup=get_voice_edit_keyboard(lang))
    await callback.answer()


## Редактирование суммы
@router.callback_query(StateFilter(VoiceTransactionStates.waiting_confirmation), F.data == "voice_edit:amount")
async def process_voice_edit_amount(callback: CallbackQuery, state: FSMContext, lang: str = "ru") -> None:
    """Начать редактирование суммы."""
    data = await state.get_data()
    lang = data.get("lang", lang)
    await state.set_state(VoiceTransactionStates.editing_amount)

    await callback.message.edit_text(
        f"\U0001f4b5 <b>{t('voice_edit_amount_title', lang)}</b>\n\n"
        f"{t('voice_edit_amount_prompt', lang)}\n\n"
        f"<i>{t('tx_amount_examples', lang)}</i>",
        reply_markup=get_voice_edit_cancel_keyboard(lang)
    )
    await callback.answer()


## Обработка новой суммы
@router.message(StateFilter(VoiceTransactionStates.editing_amount))
async def process_voice_amount_input(message: Message, state: FSMContext, lang: str = "ru") -> None:
    """Обработать ввод новой суммы."""
    from decimal import Decimal, InvalidOperation

    data = await state.get_data()
    lang = data.get("lang", lang)

    amount_str = message.text.replace(",", ".").replace("\u20bd", "").replace("$", "").replace(" ", "")

    try:
        amount = Decimal(amount_str)

        if amount <= 0:
            await message.answer(
                f"\u274c {t('voice_edit_amount_positive', lang)}",
                reply_markup=get_voice_edit_cancel_keyboard(lang)
            )
            return

        if amount > 10_000_000:
            await message.answer(
                f"\u274c {t('voice_edit_amount_too_big', lang)}",
                reply_markup=get_voice_edit_cancel_keyboard(lang)
            )
            return

        await state.update_data(amount=amount)
        await state.set_state(VoiceTransactionStates.waiting_confirmation)

        await show_voice_confirmation(message, state, lang=lang)

    except (ValueError, InvalidOperation):
        await message.answer(
            f"\u274c {t('voice_edit_amount_invalid', lang)}",
            reply_markup=get_voice_edit_cancel_keyboard(lang)
        )


## Редактирование категории
@router.callback_query(StateFilter(VoiceTransactionStates.waiting_confirmation), F.data == "voice_edit:category")
async def process_voice_edit_category(callback: CallbackQuery, state: FSMContext, lang: str = "ru") -> None:
    """Начать редактирование категории."""
    data = await state.get_data()
    lang = data.get("lang", lang)
    await state.set_state(VoiceTransactionStates.editing_category)

    category_type = CategoryType.EXPENSE if data["transaction_type"] == "expense" else CategoryType.INCOME

    categories = await get_categories(
        user_id=data["user_id"],
        category_type=category_type,
        include_default=True
    )

    categories_list = [(cat.id, cat.name, cat.emoji) for cat in categories]

    type_text = t("tx_category_of_expense", lang) if category_type == CategoryType.EXPENSE else t("tx_category_of_income", lang)

    await callback.message.edit_text(
        f"\U0001f3f7 <b>{t('voice_edit_category_title', lang)}</b>\n\n"
        f"{t('voice_edit_category_choose', lang, type=type_text)}",
        reply_markup=get_voice_categories_keyboard(categories_list, data["transaction_type"], lang)
    )
    await callback.answer()


## Выбор новой категории
@router.callback_query(StateFilter(VoiceTransactionStates.editing_category), F.data.startswith("voice_cat:"))
async def process_voice_category_selection(callback: CallbackQuery, state: FSMContext, lang: str = "ru") -> None:
    """Обработать выбор категории."""
    data = await state.get_data()
    lang = data.get("lang", lang)
    category_id = int(callback.data.split(":")[1])

    category_type = CategoryType.EXPENSE if data["transaction_type"] == "expense" else CategoryType.INCOME

    categories = await get_categories(
        user_id=data["user_id"],
        category_type=category_type,
        include_default=True
    )

    category = next((c for c in categories if c.id == category_id), None)

    if not category:
        await callback.answer(f"\u274c {t('cat_not_found', lang)}", show_alert=True)
        return

    await state.update_data(
        category_id=category.id,
        category_name=category.name,
        category_emoji=category.emoji
    )

    await state.set_state(VoiceTransactionStates.waiting_confirmation)

    await show_voice_confirmation(callback.message, state, edit=True, lang=lang)
    await callback.answer()


## Редактирование описания
@router.callback_query(StateFilter(VoiceTransactionStates.waiting_confirmation), F.data == "voice_edit:description")
async def process_voice_edit_description(callback: CallbackQuery, state: FSMContext, lang: str = "ru") -> None:
    """Начать редактирование описания."""
    data = await state.get_data()
    lang = data.get("lang", lang)
    await state.set_state(VoiceTransactionStates.editing_description)

    current_description = data.get("description", "")

    text = f"\U0001f4dd <b>{t('voice_edit_description_title', lang)}</b>\n\n"

    if current_description:
        text += f"{t('voice_edit_description_current', lang, desc=current_description)}\n\n"

    text += t("voice_edit_description_prompt", lang)

    await callback.message.edit_text(text, reply_markup=get_voice_edit_cancel_keyboard(lang))
    await callback.answer()


## Обработка описания
@router.message(StateFilter(VoiceTransactionStates.editing_description))
async def process_voice_description_input(message: Message, state: FSMContext, lang: str = "ru") -> None:
    """Обработать ввод нового описания."""
    data = await state.get_data()
    lang = data.get("lang", lang)
    description = message.text.strip()

    if description == "-":
        await state.update_data(description=None)
    else:
        if len(description) > 500:
            await message.answer(
                f"\u274c {t('voice_edit_description_too_long', lang)}",
                reply_markup=get_voice_edit_cancel_keyboard(lang)
            )
            return

        await state.update_data(description=description)

    await state.set_state(VoiceTransactionStates.waiting_confirmation)

    await show_voice_confirmation(message, state, lang=lang)


## Возврат к подтверждению
@router.callback_query(StateFilter(VoiceTransactionStates), F.data == "voice:back_to_confirm")
async def process_voice_back_to_confirm(callback: CallbackQuery, state: FSMContext, lang: str = "ru") -> None:
    """Возврат к подтверждению."""
    data = await state.get_data()
    lang = data.get("lang", lang)
    await state.set_state(VoiceTransactionStates.waiting_confirmation)
    await show_voice_confirmation(callback.message, state, edit=True, lang=lang)
    await callback.answer()


## Возврат к меню редактирования
@router.callback_query(StateFilter(VoiceTransactionStates), F.data == "voice:back_to_edit_menu")
async def process_voice_back_to_edit_menu(callback: CallbackQuery, state: FSMContext, lang: str = "ru") -> None:
    """Возврат к меню редактирования."""
    await state.set_state(VoiceTransactionStates.waiting_confirmation)
    await process_voice_edit(callback, state, lang)


## Отмена
@router.callback_query(StateFilter(VoiceTransactionStates), F.data == "voice:cancel")
async def process_voice_cancel(callback: CallbackQuery, state: FSMContext, lang: str = "ru") -> None:
    """Отмена голосовой транзакции."""
    data = await state.get_data()
    lang = data.get("lang", lang)
    await state.clear()
    await callback.message.edit_text(f"\u274c {t('tx_cancelled', lang)}")
    await callback.answer()
