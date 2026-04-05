"""
Обработчики для настроек пользователя.

Управляет настройками лимитов транзакций, смены языка и других параметров.
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from loguru import logger
from decimal import Decimal
from datetime import datetime, timezone

from bot.models import get_session, User
from bot.services.database import get_or_create_user, get_user_statistics
from bot.states.settings_states import SettingsStates
from bot.keyboards.settings_keyboards import (
    get_settings_menu_keyboard,
    get_cancel_settings_keyboard,
    get_remove_limit_keyboard
)
from bot.locales import t
from sqlalchemy import select
from config import get_settings

router = Router(name="settings")


def _settings_text(lang: str) -> str:
    """Текст меню настроек."""
    return (
        f"\u2699\ufe0f <b>{t('settings_title', lang)}</b>\n\n"
        f"{t('settings_subtitle', lang)}"
    )


## Команда /settings
@router.message(Command("settings"))
async def cmd_settings(message: Message, lang: str = "ru") -> None:
    """Открыть меню настроек (команда)."""
    logger.info(f"Пользователь {message.from_user.id} открыл настройки")

    await message.answer(
        _settings_text(lang),
        reply_markup=get_settings_menu_keyboard(lang),
        parse_mode="HTML"
    )


## Главное меню настроек
@router.callback_query(F.data == "settings:menu")
async def settings_menu(callback: CallbackQuery, lang: str = "ru") -> None:
    """Показать главное меню настроек."""
    logger.info(f"Пользователь {callback.from_user.id} открыл настройки")

    await callback.message.edit_text(
        _settings_text(lang),
        reply_markup=get_settings_menu_keyboard(lang),
        parse_mode="HTML"
    )
    await callback.answer()


## Кнопка смены языка
@router.callback_query(F.data == "settings:language")
async def settings_language(callback: CallbackQuery, lang: str = "ru") -> None:
    """Показать выбор языка."""
    from bot.handlers.common import get_language_keyboard

    await callback.message.edit_text(
        t("select_language", lang),
        reply_markup=get_language_keyboard()
    )
    await callback.answer()


## Просмотр текущих лимитов
@router.callback_query(F.data == "settings:view_limits")
async def view_limits(callback: CallbackQuery, lang: str = "ru") -> None:
    """Показать текущие лимиты."""
    user_tg = callback.from_user

    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_tg.id)
        )
        user = result.scalar_one_or_none()

        if not user:
            await callback.answer(f"\u274c {t('settings_error_save', lang)}", show_alert=True)
            return

        settings = get_settings()
        global_limit = settings.max_transaction_amount

        text = f"\U0001f4cb <b>{t('limits_title', lang)}</b>\n\n"

        text += f"\U0001f4b0 <b>{t('limits_tx_label', lang)}</b>\n"
        if user.max_transaction_limit:
            text += f"\u2514 {t('limits_tx_personal', lang, limit=f'{user.max_transaction_limit:,}')}\n\n"
        else:
            text += f"\u2514 {t('limits_tx_default', lang, limit=f'{global_limit:,}')}\n\n"

        text += f"\U0001f4ca <b>{t('limits_monthly_label', lang)}</b>\n"
        if user.monthly_limit:
            text += f"\u2514 {user.monthly_limit:,}\n\n"

            now = datetime.now(timezone.utc)
            start_month = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
            stats = await get_user_statistics(user.id, start_date=start_month)

            spent = float(stats['total_expense']) if 'total_expense' in stats else sum(
                float(v) for v in stats.get('expense_by_currency', {}).values()
            )
            remaining = user.monthly_limit - spent
            percent = (spent / user.monthly_limit * 100) if user.monthly_limit > 0 else 0

            text += f"\U0001f4b8 <b>{t('limits_spent_label', lang)}</b>\n"
            text += f"\u2514 {t('limits_spent_detail', lang, spent=f'{spent:,.0f}', limit=f'{user.monthly_limit:,}', percent=percent)}\n"
            text += f"\u2514 {t('limits_remaining', lang, remaining=f'{remaining:,.0f}')}\n\n"

            if percent >= 100:
                text += f"\u26a0\ufe0f <b>{t('limits_exceeded', lang)}</b>\n\n"
            elif percent >= 80:
                text += f"\u26a0\ufe0f <b>{t('limits_approaching', lang)}</b>\n\n"
        else:
            text += f"\u2514 {t('limits_monthly_not_set', lang)}\n\n"

        text += f"\U0001f4a1 {t('limits_hint', lang)}"

    await callback.message.edit_text(
        text,
        reply_markup=get_settings_menu_keyboard(lang),
        parse_mode="HTML"
    )
    await callback.answer()


## Установка лимита транзакции
@router.callback_query(F.data == "settings:transaction_limit")
async def set_transaction_limit(callback: CallbackQuery, state: FSMContext, lang: str = "ru") -> None:
    """Начать процесс установки лимита транзакции."""
    logger.info(f"Пользователь {callback.from_user.id} настраивает лимит транзакции")

    text = (
        f"\U0001f4b0 <b>{t('settings_tx_limit_title', lang)}</b>\n\n"
        f"{t('settings_tx_limit_prompt', lang)}"
    )

    await callback.message.edit_text(
        text,
        reply_markup=get_cancel_settings_keyboard(lang),
        parse_mode="HTML"
    )
    await state.set_state(SettingsStates.waiting_for_transaction_limit)
    await callback.answer()


## Обработка ввода лимита транзакции
@router.message(SettingsStates.waiting_for_transaction_limit)
async def process_transaction_limit(message: Message, state: FSMContext, lang: str = "ru") -> None:
    """Обработать введенный лимит транзакции."""
    user_tg = message.from_user

    try:
        limit = int(message.text.replace(" ", "").replace(",", ""))

        if limit <= 0:
            await message.answer(f"\u274c {t('settings_limit_positive', lang)}")
            return

        if limit > 1000000000:
            await message.answer(f"\u274c {t('settings_limit_too_big', lang)}")
            return

        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == user_tg.id)
            )
            user = result.scalar_one_or_none()

            if user:
                user.max_transaction_limit = limit
                await session.commit()

                logger.info(f"Пользователь {user_tg.id} установил лимит транзакции: {limit}")

                text = (
                    f"\u2705 <b>{t('settings_tx_limit_set', lang)}</b>\n\n"
                    f"{t('settings_tx_limit_set_detail', lang, limit=f'{limit:,}')}"
                )

                await message.answer(
                    text,
                    reply_markup=get_settings_menu_keyboard(lang),
                    parse_mode="HTML"
                )
            else:
                await message.answer(f"\u274c {t('settings_error_save', lang)}")

        await state.clear()

    except ValueError:
        await message.answer(
            f"\u274c {t('settings_limit_invalid', lang, example='50000')}"
        )


## Установка месячного лимита
@router.callback_query(F.data == "settings:monthly_limit")
async def set_monthly_limit(callback: CallbackQuery, state: FSMContext, lang: str = "ru") -> None:
    """Начать процесс установки месячного лимита."""
    logger.info(f"Пользователь {callback.from_user.id} настраивает месячный лимит")

    text = (
        f"\U0001f4ca <b>{t('settings_monthly_title', lang)}</b>\n\n"
        f"{t('settings_monthly_prompt', lang)}"
    )

    await callback.message.edit_text(
        text,
        reply_markup=get_cancel_settings_keyboard(lang),
        parse_mode="HTML"
    )
    await state.set_state(SettingsStates.waiting_for_monthly_limit)
    await callback.answer()


## Обработка ввода месячного лимита
@router.message(SettingsStates.waiting_for_monthly_limit)
async def process_monthly_limit(message: Message, state: FSMContext, lang: str = "ru") -> None:
    """Обработать введенный месячный лимит."""
    user_tg = message.from_user

    try:
        limit = int(message.text.replace(" ", "").replace(",", ""))

        if limit <= 0:
            await message.answer(f"\u274c {t('settings_limit_positive', lang)}")
            return

        if limit > 1000000000:
            await message.answer(f"\u274c {t('settings_limit_too_big', lang)}")
            return

        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == user_tg.id)
            )
            user = result.scalar_one_or_none()

            if user:
                user.monthly_limit = limit
                await session.commit()

                logger.info(f"Пользователь {user_tg.id} установил месячный лимит: {limit}")

                text = (
                    f"\u2705 <b>{t('settings_monthly_set', lang)}</b>\n\n"
                    f"{t('settings_monthly_set_detail', lang, limit=f'{limit:,}')}"
                )

                await message.answer(
                    text,
                    reply_markup=get_settings_menu_keyboard(lang),
                    parse_mode="HTML"
                )
            else:
                await message.answer(f"\u274c {t('settings_error_save', lang)}")

        await state.clear()

    except ValueError:
        await message.answer(
            f"\u274c {t('settings_limit_invalid', lang, example='100000')}"
        )


## Удаление лимита транзакции
@router.callback_query(F.data == "settings:remove_transaction_limit")
async def remove_transaction_limit(callback: CallbackQuery, lang: str = "ru") -> None:
    """Удалить персональный лимит транзакции."""
    user_tg = callback.from_user

    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_tg.id)
        )
        user = result.scalar_one_or_none()

        if user:
            user.max_transaction_limit = None
            await session.commit()

            logger.info(f"Пользователь {user_tg.id} удалил лимит транзакции")

            settings = get_settings()

            text = (
                f"\u2705 <b>{t('settings_tx_limit_removed', lang)}</b>\n\n"
                f"{t('settings_tx_limit_removed_detail', lang, limit=f'{settings.max_transaction_amount:,}')}"
            )

            await callback.message.edit_text(
                text,
                reply_markup=get_settings_menu_keyboard(lang),
                parse_mode="HTML"
            )
        else:
            await callback.answer(f"\u274c", show_alert=True)

    await callback.answer()


## Удаление месячного лимита
@router.callback_query(F.data == "settings:remove_monthly_limit")
async def remove_monthly_limit(callback: CallbackQuery, lang: str = "ru") -> None:
    """Удалить месячный лимит трат."""
    user_tg = callback.from_user

    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_tg.id)
        )
        user = result.scalar_one_or_none()

        if user:
            user.monthly_limit = None
            await session.commit()

            logger.info(f"Пользователь {user_tg.id} удалил месячный лимит")

            text = (
                f"\u2705 <b>{t('settings_monthly_removed', lang)}</b>\n\n"
                f"{t('settings_monthly_removed_detail', lang)}"
            )

            await callback.message.edit_text(
                text,
                reply_markup=get_settings_menu_keyboard(lang),
                parse_mode="HTML"
            )
        else:
            await callback.answer(f"\u274c", show_alert=True)

    await callback.answer()


## Отмена настройки
@router.callback_query(F.data == "settings:cancel")
async def cancel_settings(callback: CallbackQuery, state: FSMContext, lang: str = "ru") -> None:
    """Отменить изменение настроек."""
    await state.clear()

    await callback.message.edit_text(
        f"\u274c {t('settings_cancel', lang)}",
        reply_markup=get_settings_menu_keyboard(lang)
    )
    await callback.answer()


## Обработчик Reply кнопки "Настройки"
@router.message(F.text.in_({"\u2699\ufe0f Настройки", "\u2699\ufe0f Settings"}))
async def handle_settings_button(message: Message, lang: str = "ru") -> None:
    """Открыть меню настроек (Reply кнопка)."""
    logger.info(f"Пользователь {message.from_user.id} открыл настройки через Reply кнопку")

    await message.answer(
        _settings_text(lang),
        reply_markup=get_settings_menu_keyboard(lang),
        parse_mode="HTML"
    )
