"""
Обработчики для экспорта данных.

Содержит handlers для:
- Команды /export
- Выбора периода экспорта
- Генерации и отправки Excel файла
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from loguru import logger

from bot.states.export_states import ExportStates
from bot.keyboards.export_keyboards import get_export_period_keyboard
from bot.keyboards.view_keyboards import get_main_menu_keyboard
from bot.services.database import get_or_create_user
from bot.services.export_service import generate_transactions_excel, cleanup_export_file
from bot.locales import t


router = Router(name="export")


## Команда /export - начало экспорта
@router.message(Command("export"))
async def cmd_export(message: Message, state: FSMContext, lang: str = "ru") -> None:
    """
    Обработчик команды /export.

    :param message: Сообщение от пользователя
    :param state: Контекст FSM
    :param lang: Код языка пользователя
    :return: None
    """
    user = await get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )

    logger.info(f"Пользователь {user.id} запросил экспорт данных")

    await state.set_state(ExportStates.selecting_period)

    await message.answer(
        f"\U0001f4e4 <b>{t('export_title', lang)}</b>\n\n"
        f"{t('export_choose_period', lang)}",
        reply_markup=get_export_period_keyboard(lang)
    )


## Callback для экспорта из меню настроек
@router.callback_query(F.data == "menu:export")
async def show_export_menu(callback: CallbackQuery, state: FSMContext, lang: str = "ru") -> None:
    """
    Показать меню экспорта (callback из главного меню).

    :param callback: Callback от inline кнопки
    :param state: Контекст FSM
    :param lang: Код языка пользователя
    :return: None
    """
    user = await get_or_create_user(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        last_name=callback.from_user.last_name,
    )

    logger.info(f"Пользователь {user.id} открыл меню экспорта")

    await state.set_state(ExportStates.selecting_period)

    await callback.message.edit_text(
        f"\U0001f4e4 <b>{t('export_title', lang)}</b>\n\n"
        f"{t('export_choose_period', lang)}",
        reply_markup=get_export_period_keyboard(lang)
    )
    await callback.answer()


## Обработка выбора периода
@router.callback_query(F.data.startswith("export:"))
async def handle_export_period(callback: CallbackQuery, state: FSMContext, lang: str = "ru") -> None:
    """
    Обработать выбор периода для экспорта.

    :param callback: Callback от inline кнопки
    :param state: Контекст FSM
    :param lang: Код языка пользователя
    :return: None
    """
    period = callback.data.split(":")[1]

    user = await get_or_create_user(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        last_name=callback.from_user.last_name,
    )

    # Определяем период
    now = datetime.now(timezone.utc)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = now

    period_key_map = {
        "today": "export_period_today",
        "yesterday": "export_period_yesterday",
        "week": "export_period_week",
        "month": "export_period_month",
        "year": "export_period_year",
        "all": "export_period_all",
    }
    period_name = t(period_key_map.get(period, "export_period_all"), lang)

    if period == "today":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "yesterday":
        yesterday = now - timedelta(days=1)
        start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif period == "week":
        start_date = now - timedelta(days=7)
    elif period == "month":
        start_date = now - timedelta(days=30)
    elif period == "year":
        start_date = now - timedelta(days=365)
    elif period == "all":
        start_date = None
        end_date = None

    # Уведомляем о начале генерации
    await callback.message.edit_text(
        f"\u23f3 <b>{t('export_generating', lang, period=period_name)}</b>\n\n"
        f"{t('export_generating_wait', lang)}"
    )
    await callback.answer()

    try:
        # Генерируем файл
        file_path = await generate_transactions_excel(
            user_id=user.id,
            start_date=start_date,
            end_date=end_date,
            lang=lang
        )

        # Отправляем файл
        document = FSInputFile(file_path)

        await callback.message.answer_document(
            document=document,
            caption=(
                f"\u2705 <b>{t('export_done', lang)}</b>\n\n"
                f"\U0001f4ca {t('export_report', lang, period=period_name)}\n"
                f"\U0001f4c5 {t('export_date', lang, date=now.strftime('%d.%m.%Y %H:%M'))}"
            )
        )

        # Показываем главное меню
        await callback.message.answer(
            f"\U0001f4cb <b>{t('export_what_next', lang)}</b>",
            reply_markup=get_main_menu_keyboard(lang)
        )

        logger.success(f"Файл экспорта отправлен пользователю {user.id}")

        # Удаляем временный файл
        cleanup_export_file(file_path)

    except Exception as e:
        from bot.utils.sanitizer import sanitize_exception_message
        safe_error = sanitize_exception_message(e)
        logger.error(f"Ошибка при генерации экспорта для пользователя {user.id}: {safe_error}")

        await callback.message.answer(
            f"\u274c <b>{t('export_error', lang)}</b>\n\n"
            f"{t('export_error_detail', lang)}",
            reply_markup=get_main_menu_keyboard(lang)
        )

    finally:
        await state.clear()


## Обработчик Reply кнопки "Экспорт" / "Export"
@router.message(F.text.in_({f"\U0001f4e4 {t('btn_export', 'ru')}", f"\U0001f4e4 {t('btn_export', 'en')}"}))
async def handle_export_button(message: Message, state: FSMContext, lang: str = "ru") -> None:
    """
    Начать процесс экспорта (Reply кнопка).

    :param message: Сообщение от пользователя
    :param state: Контекст FSM
    :param lang: Код языка пользователя
    :return: None
    """
    user = await get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )

    logger.info(f"Пользователь {user.id} запросил экспорт через Reply кнопку")

    await state.update_data(user_id=user.id)
    await state.set_state(ExportStates.selecting_period)

    await message.answer(
        f"\U0001f4e4 <b>{t('export_title', lang)}</b>\n\n"
        f"{t('export_choose_period', lang)}",
        reply_markup=get_export_period_keyboard(lang)
    )
