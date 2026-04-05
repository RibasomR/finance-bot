"""
Обработчики для просмотра транзакций и статистики.

Поддержка мультиязычности через locales.
"""

import math
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Optional

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from loguru import logger

from bot.states import ViewTransactionsStates, EditTransactionStates, AddTransactionStates
from bot.keyboards.view_keyboards import (
    get_main_menu_keyboard,
    get_stats_keyboard,
    get_transactions_navigation_keyboard,
    get_transaction_actions_keyboard,
    get_delete_confirmation_keyboard,
    get_period_filter_keyboard,
    get_edit_field_keyboard,
    get_transaction_inline_button,
)
from bot.keyboards.transaction_keyboards import get_categories_keyboard, get_cancel_keyboard
from bot.keyboards.reply_keyboards import get_main_reply_keyboard
from bot.services.database import (
    get_or_create_user,
    get_user_transactions_with_filters,
    count_user_transactions,
    get_transaction_by_id,
    delete_transaction,
    get_user_statistics,
    get_top_expense_categories,
    update_transaction,
    get_categories,
)
from bot.models import TransactionType, CategoryType
from bot.locales import t, translate_category_name


router = Router(name="view")

TRANSACTIONS_PER_PAGE = 10


## Команда /menu
@router.message(Command("menu"))
async def cmd_menu(message: Message, lang: str = "ru") -> None:
    """Показать главное меню."""
    await get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )

    await message.answer(
        f"\U0001f4cb <b>{t('main_menu_title', lang)}</b>\n\n"
        f"{t('main_menu_subtitle', lang)} \U0001f447",
        reply_markup=get_main_reply_keyboard(lang)
    )


## Callback главного меню
@router.callback_query(F.data == "menu:main")
async def show_main_menu(callback: CallbackQuery, state: FSMContext, lang: str = "ru") -> None:
    """Показать главное меню (callback)."""
    await state.clear()

    await callback.message.edit_text(
        f"\U0001f4cb <b>{t('main_menu_title', lang)}</b>\n\n"
        f"{t('main_menu_action', lang)}",
        reply_markup=get_main_menu_keyboard(lang)
    )
    await callback.answer()


## Команда /stats
@router.message(Command("stats"))
async def cmd_stats(message: Message, lang: str = "ru") -> None:
    """Показать статистику."""
    user = await get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )
    await show_statistics(message, user.id, lang=lang)


## Статистика (callback)
@router.callback_query(F.data == "menu:stats")
async def show_stats_callback(callback: CallbackQuery, lang: str = "ru") -> None:
    """Показать статистику (callback)."""
    user = await get_or_create_user(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        last_name=callback.from_user.last_name,
    )
    await show_statistics(callback.message, user.id, edit=True, lang=lang)
    await callback.answer()


## Настройки (callback)
@router.callback_query(F.data == "menu:settings")
async def show_settings_menu(callback: CallbackQuery, lang: str = "ru") -> None:
    """Открыть меню настроек."""
    from bot.keyboards.settings_keyboards import get_settings_menu_keyboard

    text = (
        f"\u2699\ufe0f <b>{t('settings_title', lang)}</b>\n\n"
        f"{t('settings_subtitle', lang)}"
    )

    await callback.message.edit_text(
        text,
        reply_markup=get_settings_menu_keyboard(lang),
        parse_mode="HTML"
    )
    await callback.answer()


## Категории (callback)
@router.callback_query(F.data == "menu:categories")
async def show_categories_menu(callback: CallbackQuery, lang: str = "ru") -> None:
    """Открыть меню категорий."""
    from bot.keyboards.category_keyboards import get_category_management_menu

    text = (
        f"\U0001f3f7\ufe0f <b>{t('cat_management_title', lang)}</b>\n\n"
        f"{t('cat_management_subtitle', lang)}"
    )

    await callback.message.edit_text(
        text,
        reply_markup=get_category_management_menu(lang),
        parse_mode="HTML"
    )
    await callback.answer()


## Функция статистики
async def show_statistics(
    message: Message,
    user_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    edit: bool = False,
    lang: str = "ru"
) -> None:
    """Отобразить статистику."""
    stats = await get_user_statistics(user_id, start_date, end_date)
    top_categories = await get_top_expense_categories(user_id, start_date, end_date, limit=3)

    if not start_date and not end_date:
        period_text = t("stats_period_all", lang)
    else:
        period_text = t("stats_period_selected", lang)

    text = f"\U0001f4ca <b>{t('stats_title', lang, period=period_text)}</b>\n\n"

    text += f"\U0001f4b0 <b>{t('stats_income', lang)}</b>\n"
    if stats['income_by_currency']:
        for currency, amount in stats['income_by_currency'].items():
            symbol = "\u20bd" if currency == "RUB" else "$"
            text += f"   +{float(amount):.2f} {symbol}\n"
    else:
        text += f"   {t('stats_no_income', lang)}\n"
    text += f"   {t('stats_operations', lang, count=stats['income_count'])}\n\n"

    text += f"\U0001f4b8 <b>{t('stats_expense', lang)}</b>\n"
    if stats['expense_by_currency']:
        for currency, amount in stats['expense_by_currency'].items():
            symbol = "\u20bd" if currency == "RUB" else "$"
            text += f"   -{float(amount):.2f} {symbol}\n"
    else:
        text += f"   {t('stats_no_expense', lang)}\n"
    text += f"   {t('stats_operations', lang, count=stats['expense_count'])}\n\n"

    text += f"\U0001f49a <b>{t('stats_balance', lang)}</b>\n"
    all_currencies = set(stats['income_by_currency'].keys()) | set(stats['expense_by_currency'].keys())
    if all_currencies:
        for currency in sorted(all_currencies):
            income = stats['income_by_currency'].get(currency, Decimal('0'))
            expense = stats['expense_by_currency'].get(currency, Decimal('0'))
            balance = income - expense
            symbol = "\u20bd" if currency == "RUB" else "$"
            sign = "+" if balance >= 0 else ""
            text += f"   {sign}{float(balance):.2f} {symbol}\n"
    else:
        text += "   0.00 \u20bd\n"

    if top_categories:
        text += f"\n\U0001f3c6 <b>{t('stats_top_categories', lang)}</b>\n"
        for i, cat in enumerate(top_categories, 1):
            symbol = "\u20bd" if cat['currency'] == "RUB" else "$"
            cat_display = translate_category_name(cat['name'], lang)
            text += f"{i}. {cat['emoji']} {cat_display}: {float(cat['total']):.2f} {symbol}\n"

    if edit:
        await message.edit_text(text, reply_markup=get_stats_keyboard(lang))
    else:
        await message.answer(text, reply_markup=get_stats_keyboard(lang))


## Просмотр транзакций
@router.message(Command("transactions"))
async def cmd_transactions(message: Message, lang: str = "ru") -> None:
    """Показать все транзакции."""
    user = await get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )
    await show_transactions_list(message, user.id, page=1, transaction_type=None, lang=lang)


## Callback для меню
@router.callback_query(F.data.startswith("menu:"))
async def handle_menu_callback(callback: CallbackQuery, lang: str = "ru") -> None:
    """Обработать выбор в меню."""
    action = callback.data.split(":")[1]

    user = await get_or_create_user(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        last_name=callback.from_user.last_name,
    )

    if action == "all":
        await show_transactions_list(callback.message, user.id, page=1, edit=True, lang=lang)
    elif action == "income":
        await show_transactions_list(
            callback.message, user.id, page=1, transaction_type=TransactionType.INCOME, edit=True, lang=lang
        )
    elif action == "expense":
        await show_transactions_list(
            callback.message, user.id, page=1, transaction_type=TransactionType.EXPENSE, edit=True, lang=lang
        )
    elif action == "period":
        await callback.message.edit_text(
            f"\U0001f4c5 <b>{t('period_title', lang)}</b>\n\n"
            f"{t('period_choose', lang)}",
            reply_markup=get_period_filter_keyboard(lang)
        )
    elif action == "settings":
        pass  # Handled by separate handler

    await callback.answer()


## Список транзакций
async def show_transactions_list(
    message: Message,
    user_id: int,
    page: int = 1,
    transaction_type: Optional[TransactionType] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    edit: bool = False,
    lang: str = "ru"
) -> None:
    """Отобразить список транзакций с пагинацией."""
    total_count = await count_user_transactions(
        user_id, transaction_type, start_date, end_date
    )

    if total_count == 0:
        text = f"\U0001f4dd <b>{t('view_no_transactions', lang)}</b>\n\n"
        if transaction_type == TransactionType.INCOME:
            text += t("view_no_income", lang)
        elif transaction_type == TransactionType.EXPENSE:
            text += t("view_no_expense", lang)
        else:
            text += t("view_no_any", lang)

        if edit:
            await message.edit_text(text, reply_markup=get_main_menu_keyboard(lang))
        else:
            await message.answer(text, reply_markup=get_main_menu_keyboard(lang))
        return

    total_pages = math.ceil(total_count / TRANSACTIONS_PER_PAGE)
    offset = (page - 1) * TRANSACTIONS_PER_PAGE

    transactions = await get_user_transactions_with_filters(
        user_id=user_id,
        transaction_type=transaction_type,
        start_date=start_date,
        end_date=end_date,
        limit=TRANSACTIONS_PER_PAGE,
        offset=offset
    )

    if transaction_type == TransactionType.INCOME:
        header = f"\U0001f4b0 <b>{t('view_income_title', lang)}</b>"
    elif transaction_type == TransactionType.EXPENSE:
        header = f"\U0001f4b8 <b>{t('view_expense_title', lang)}</b>"
    else:
        header = f"\U0001f4dd <b>{t('view_all_title', lang)}</b>"

    text = f"{header}\n\n"
    text += f"\U0001f4c4 {t('view_page', lang, page=page, total=total_pages)}\n\n"
    text += f"\U0001f446 {t('view_tap_to_edit', lang)}"

    type_str = None
    if transaction_type == TransactionType.INCOME:
        type_str = "income"
    elif transaction_type == TransactionType.EXPENSE:
        type_str = "expense"

    transactions_info = []
    for tr in transactions:
        currency_symbol = "\u20bd" if tr.currency == "RUB" else "$"
        description = tr.description if tr.description else ""
        cat_display = translate_category_name(tr.category.name, lang)

        transactions_info.append({
            "id": tr.id,
            "description": description,
            "amount": float(tr.amount),
            "category_name": cat_display,
            "currency_symbol": currency_symbol,
        })

    keyboard = get_transactions_navigation_keyboard(
        page=page,
        total_pages=total_pages,
        transactions_info=transactions_info,
        transaction_type=type_str,
        lang=lang
    )

    if edit:
        await message.edit_text(text, reply_markup=keyboard)
    else:
        await message.answer(text, reply_markup=keyboard)


## Навигация
@router.callback_query(F.data.startswith("nav:"))
async def handle_navigation(callback: CallbackQuery, lang: str = "ru") -> None:
    """Навигация по страницам."""
    parts = callback.data.split(":")
    action = parts[1]

    if action == "page":
        await callback.answer()
        return

    page = int(parts[2])
    transaction_type = None

    if len(parts) > 3:
        type_str = parts[3]
        if type_str == "income":
            transaction_type = TransactionType.INCOME
        elif type_str == "expense":
            transaction_type = TransactionType.EXPENSE

    user = await get_or_create_user(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        last_name=callback.from_user.last_name,
    )

    await show_transactions_list(
        callback.message, user.id, page=page, transaction_type=transaction_type, edit=True, lang=lang
    )
    await callback.answer()


## Фильтр по периоду
@router.callback_query(F.data.startswith("period:"))
async def handle_period_filter(callback: CallbackQuery, lang: str = "ru") -> None:
    """Обработать выбор периода."""
    period = callback.data.split(":")[1]

    user = await get_or_create_user(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        last_name=callback.from_user.last_name,
    )

    now = datetime.now(timezone.utc)
    start_date = None
    end_date = now

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

    await show_transactions_list(
        callback.message, user.id, page=1, start_date=start_date, end_date=end_date, edit=True, lang=lang
    )
    await callback.answer()


## Удаление транзакции
@router.callback_query(F.data.startswith("delete:"))
async def handle_delete_transaction(callback: CallbackQuery, state: FSMContext, lang: str = "ru") -> None:
    """Обработать удаление транзакции."""
    parts = callback.data.split(":")
    action = parts[1]

    if action == "cancel":
        await state.clear()
        await callback.message.edit_text(
            f"\u274c {t('delete_cancelled', lang)}",
            reply_markup=get_main_menu_keyboard(lang)
        )
        await callback.answer()
        return

    transaction_id = int(parts[-1])

    user = await get_or_create_user(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        last_name=callback.from_user.last_name,
    )

    if action == "confirm":
        success = await delete_transaction(transaction_id, user.id)

        if success:
            await callback.message.edit_text(
                f"\u2705 <b>{t('delete_success', lang)}</b>",
                reply_markup=get_main_menu_keyboard(lang)
            )
        else:
            await callback.message.edit_text(
                f"\u274c {t('delete_not_found', lang)}",
                reply_markup=get_main_menu_keyboard(lang)
            )

        await state.clear()
    else:
        transaction = await get_transaction_by_id(transaction_id, user.id)

        if not transaction:
            await callback.answer(f"\u274c {t('delete_not_found', lang)}", show_alert=True)
            return

        type_emoji = "\U0001f4b0" if transaction.type == TransactionType.INCOME else "\U0001f4b8"
        sign = "+" if transaction.type == TransactionType.INCOME else "-"
        currency_symbol = "\u20bd" if transaction.currency == "RUB" else "$"
        cat_display = translate_category_name(transaction.category.name, lang)

        text = (
            f"\u26a0\ufe0f <b>{t('delete_confirm_title', lang)}</b>\n\n"
            f"{type_emoji} <b>{sign}{float(transaction.amount):.2f} {currency_symbol}</b>\n"
            f"{transaction.category.emoji} {cat_display}\n"
        )

        if transaction.description:
            text += f"\U0001f4ac {transaction.description}\n"

        text += f"\n<b>{t('delete_confirm_question', lang)}</b>"

        await callback.message.edit_text(
            text,
            reply_markup=get_delete_confirmation_keyboard(transaction_id, lang)
        )

    await callback.answer()


## Редактирование транзакции
@router.callback_query(F.data.startswith("edit:"))
async def handle_edit_transaction(callback: CallbackQuery, state: FSMContext, lang: str = "ru") -> None:
    """Обработать редактирование транзакции."""
    parts = callback.data.split(":")
    action = parts[1]

    if action == "cancel":
        await state.clear()
        await callback.message.edit_text(
            f"\u274c {t('edit_cancelled', lang)}",
            reply_markup=get_main_menu_keyboard(lang)
        )
        await callback.answer()
        return

    user = await get_or_create_user(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        last_name=callback.from_user.last_name,
    )

    if action == "field":
        field = parts[2]
        transaction_id = int(parts[3])

        transaction = await get_transaction_by_id(transaction_id, user.id)

        if not transaction:
            await callback.answer(f"\u274c {t('delete_not_found', lang)}", show_alert=True)
            return

        await state.update_data(transaction_id=transaction_id, user_id=user.id, lang=lang)

        if field == "amount":
            await state.set_state(EditTransactionStates.editing_amount)
            currency_symbol = "\u20bd" if transaction.currency == "RUB" else "$"
            await callback.message.edit_text(
                f"\U0001f4b5 <b>{t('edit_amount_title', lang)}</b>\n\n"
                f"{t('edit_amount_current', lang, amount=f'{float(transaction.amount):.2f}', currency=currency_symbol)}\n\n"
                f"{t('edit_amount_enter', lang)}",
                reply_markup=get_cancel_keyboard(lang=lang)
            )
        elif field == "category":
            await state.set_state(EditTransactionStates.editing_category)

            category_type = CategoryType.EXPENSE if transaction.type == TransactionType.EXPENSE else CategoryType.INCOME
            categories = await get_categories(
                user_id=user.id,
                category_type=category_type,
                include_default=True
            )

            categories_list = [(cat.id, cat.name, cat.emoji) for cat in categories]
            type_str = "expense" if transaction.type == TransactionType.EXPENSE else "income"
            cat_display = translate_category_name(transaction.category.name, lang)

            await callback.message.edit_text(
                f"\U0001f3f7 <b>{t('edit_category_title', lang)}</b>\n\n"
                f"{t('edit_category_current', lang, emoji=transaction.category.emoji, name=cat_display)}\n\n"
                f"{t('edit_category_choose', lang)}",
                reply_markup=get_categories_keyboard(categories_list, type_str, lang)
            )
        elif field == "description":
            await state.set_state(EditTransactionStates.editing_description)

            desc_text = transaction.description if transaction.description else t("edit_description_not_set", lang)

            await callback.message.edit_text(
                f"\U0001f4dd <b>{t('edit_description_title', lang)}</b>\n\n"
                f"{t('edit_description_current', lang, desc=desc_text)}\n\n"
                f"{t('edit_description_enter', lang)}",
                reply_markup=get_cancel_keyboard(skip_button=True, lang=lang)
            )
    else:
        transaction_id = int(parts[1])

        transaction = await get_transaction_by_id(transaction_id, user.id)

        if not transaction:
            await callback.answer(f"\u274c {t('delete_not_found', lang)}", show_alert=True)
            return

        type_emoji = "\U0001f4b0" if transaction.type == TransactionType.INCOME else "\U0001f4b8"
        sign = "+" if transaction.type == TransactionType.INCOME else "-"
        currency_symbol = "\u20bd" if transaction.currency == "RUB" else "$"
        cat_display = translate_category_name(transaction.category.name, lang)

        text = (
            f"\u270f\ufe0f <b>{t('edit_title', lang)}</b>\n\n"
            f"{type_emoji} <b>{sign}{float(transaction.amount):.2f} {currency_symbol}</b>\n"
            f"{transaction.category.emoji} {cat_display}\n"
        )

        if transaction.description:
            text += f"\U0001f4ac {transaction.description}\n"

        text += f"\n<b>{t('edit_what_change', lang)}</b>"

        await callback.message.edit_text(
            text,
            reply_markup=get_edit_field_keyboard(transaction_id, lang)
        )

    await callback.answer()


## Ввод новой суммы
@router.message(StateFilter(EditTransactionStates.editing_amount))
async def process_edit_amount(message: Message, state: FSMContext, lang: str = "ru") -> None:
    """Обработать ввод новой суммы."""
    from bot.utils.validators import validate_amount

    data = await state.get_data()
    lang = data.get("lang", lang)

    is_valid, amount, error_msg = validate_amount(message.text)

    if not is_valid:
        await message.answer(
            f"{error_msg}\n\n{t('tx_error_enter_valid', lang)}",
            reply_markup=get_cancel_keyboard(lang=lang)
        )
        return

    transaction_id = data["transaction_id"]
    user_id = data["user_id"]

    transaction = await update_transaction(
        transaction_id=transaction_id,
        user_id=user_id,
        amount=amount
    )

    if transaction:
        currency_symbol = "\u20bd" if transaction.currency == "RUB" else "$"
        await message.answer(
            f"\u2705 <b>{t('edit_amount_updated', lang)}</b>\n\n"
            f"{t('edit_amount_new', lang, amount=f'{float(transaction.amount):.2f}', currency=currency_symbol)}",
            reply_markup=get_main_menu_keyboard(lang)
        )
    else:
        await message.answer(
            f"\u274c {t('edit_error', lang)}",
            reply_markup=get_main_menu_keyboard(lang)
        )

    await state.clear()


## Выбор новой категории
@router.callback_query(StateFilter(EditTransactionStates.editing_category), F.data.startswith("category:"))
async def process_edit_category(callback: CallbackQuery, state: FSMContext, lang: str = "ru") -> None:
    """Обработать выбор новой категории."""
    data = await state.get_data()
    lang = data.get("lang", lang)
    category_id = int(callback.data.split(":")[1])

    transaction_id = data["transaction_id"]
    user_id = data["user_id"]

    transaction = await update_transaction(
        transaction_id=transaction_id,
        user_id=user_id,
        category_id=category_id
    )

    if transaction:
        cat_display = translate_category_name(transaction.category.name, lang)
        await callback.message.edit_text(
            f"\u2705 <b>{t('edit_category_updated', lang)}</b>\n\n"
            f"{t('edit_category_new', lang, emoji=transaction.category.emoji, name=cat_display)}",
            reply_markup=get_main_menu_keyboard(lang)
        )
    else:
        await callback.message.edit_text(
            f"\u274c {t('edit_error', lang)}",
            reply_markup=get_main_menu_keyboard(lang)
        )

    await state.clear()
    await callback.answer()


## Ввод нового описания
@router.message(StateFilter(EditTransactionStates.editing_description))
async def process_edit_description(message: Message, state: FSMContext, lang: str = "ru") -> None:
    """Обработать ввод нового описания."""
    data = await state.get_data()
    lang = data.get("lang", lang)
    description = message.text.strip()

    if len(description) > 500:
        await message.answer(
            f"\u274c {t('voice_edit_description_too_long', lang)}",
            reply_markup=get_cancel_keyboard(skip_button=True, lang=lang)
        )
        return

    transaction_id = data["transaction_id"]
    user_id = data["user_id"]

    transaction = await update_transaction(
        transaction_id=transaction_id,
        user_id=user_id,
        description=description
    )

    if transaction:
        await message.answer(
            f"\u2705 <b>{t('edit_description_updated', lang)}</b>\n\n"
            f"{t('edit_description_new', lang, desc=transaction.description)}",
            reply_markup=get_main_menu_keyboard(lang)
        )
    else:
        await message.answer(
            f"\u274c {t('edit_error', lang)}",
            reply_markup=get_main_menu_keyboard(lang)
        )

    await state.clear()


## Пропуск описания (удаление)
@router.callback_query(StateFilter(EditTransactionStates.editing_description), F.data == "skip")
async def process_edit_skip_description(callback: CallbackQuery, state: FSMContext, lang: str = "ru") -> None:
    """Удалить описание транзакции."""
    data = await state.get_data()
    lang = data.get("lang", lang)
    transaction_id = data["transaction_id"]
    user_id = data["user_id"]

    transaction = await update_transaction(
        transaction_id=transaction_id,
        user_id=user_id,
        description=None
    )

    if transaction:
        await callback.message.edit_text(
            f"\u2705 <b>{t('edit_description_removed', lang)}</b>",
            reply_markup=get_main_menu_keyboard(lang)
        )
    else:
        await callback.message.edit_text(
            f"\u274c {t('edit_error', lang)}",
            reply_markup=get_main_menu_keyboard(lang)
        )

    await state.clear()
    await callback.answer()


## Reply кнопка "Доходы"
@router.message(F.text.in_({"\U0001f4b0 Доходы", "\U0001f4b0 Income"}))
async def handle_income_button(message: Message, lang: str = "ru") -> None:
    """Показать доходы."""
    user = await get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )
    await show_transactions_list(message, user.id, page=1, transaction_type=TransactionType.INCOME, lang=lang)


## Reply кнопка "Расходы"
@router.message(F.text.in_({"\U0001f4b8 Расходы", "\U0001f4b8 Expenses"}))
async def handle_expense_button(message: Message, lang: str = "ru") -> None:
    """Показать расходы."""
    user = await get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )
    await show_transactions_list(message, user.id, page=1, transaction_type=TransactionType.EXPENSE, lang=lang)


## Reply кнопка "Статистика"
@router.message(F.text.in_({"\U0001f4ca Статистика", "\U0001f4ca Statistics"}))
async def handle_stats_button(message: Message, lang: str = "ru") -> None:
    """Показать статистику."""
    user = await get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )
    await show_statistics(message, user.id, lang=lang)


## Reply кнопка "Все транзакции"
@router.message(F.text.in_({"\U0001f4dd Все транзакции", "\U0001f4dd All transactions"}))
async def handle_all_transactions_button(message: Message, lang: str = "ru") -> None:
    """Показать все транзакции."""
    user = await get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )
    await show_transactions_list(message, user.id, page=1, transaction_type=None, lang=lang)


## Reply кнопка "За период"
@router.message(F.text.in_({"\U0001f4c5 За период", "\U0001f4c5 By period"}))
async def handle_period_button(message: Message, lang: str = "ru") -> None:
    """Показать фильтр по периоду."""
    await message.answer(
        f"\U0001f4c5 <b>{t('period_title', lang)}</b>\n\n"
        f"{t('period_choose', lang)}",
        reply_markup=get_period_filter_keyboard(lang)
    )
