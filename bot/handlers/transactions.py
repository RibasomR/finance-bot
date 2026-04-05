"""
Обработчики для работы с транзакциями.

Содержит хендлеры для добавления транзакций (пошаговый и быстрый ввод).
Поддержка мультиязычности.
"""

import re
from decimal import Decimal, InvalidOperation
from typing import Optional

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from loguru import logger

from bot.states import AddTransactionStates
from bot.keyboards.transaction_keyboards import (
    get_transaction_type_keyboard,
    get_categories_keyboard,
    get_confirmation_keyboard,
    get_cancel_keyboard,
)
from bot.keyboards.view_keyboards import get_edit_transaction_button
from bot.services.database import (
    get_or_create_user,
    get_categories,
    get_category_by_id,
    create_custom_category,
    create_transaction,
)
from bot.models import CategoryType, TransactionType
from bot.utils.validators import (
    validate_amount,
    validate_category_name,
    validate_description,
    sanitize_text,
)
from bot.locales import t, translate_category_name


router = Router(name="transactions")


## Команда /add
@router.message(Command("add"))
async def cmd_add_transaction(message: Message, state: FSMContext, lang: str = "ru") -> None:
    """Обработчик команды /add для добавления транзакции."""
    user = await get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )

    command_args = message.text.split(maxsplit=1)

    if len(command_args) > 1:
        await handle_quick_add(message, state, user.id, command_args[1], lang)
    else:
        await state.set_state(AddTransactionStates.choosing_type)
        await state.update_data(user_id=user.id, lang=lang)

        await message.answer(
            f"\U0001f4b0 <b>{t('tx_add_title', lang)}</b>\n\n"
            f"{t('tx_choose_type', lang)}",
            reply_markup=get_transaction_type_keyboard(lang)
        )


## Быстрый ввод транзакции
async def handle_quick_add(message: Message, state: FSMContext, user_id: int, args_text: str, lang: str = "ru") -> None:
    """Обработка быстрого ввода транзакции."""
    parts = args_text.split()

    if len(parts) < 2:
        await message.answer(f"\u274c {t('tx_error_not_enough_params', lang)}")
        return

    type_str = parts[0].lower()
    expense_words = t("quick_expense_words", lang)
    income_words = t("quick_income_words", lang)

    if type_str in expense_words:
        transaction_type = TransactionType.EXPENSE
        category_type = CategoryType.EXPENSE
    elif type_str in income_words:
        transaction_type = TransactionType.INCOME
        category_type = CategoryType.INCOME
    else:
        await message.answer(f"\u274c {t('tx_error_unknown_type', lang)}")
        return

    amount_str = parts[1].replace(",", ".").replace("\u20bd", "").replace("$", "").replace(" ", "")
    try:
        amount = Decimal(amount_str)
        if amount <= 0:
            raise ValueError()
    except (ValueError, InvalidOperation):
        await message.answer(f"\u274c {t('tx_error_invalid_amount', lang)}")
        return

    category = None
    description_parts = []

    if len(parts) > 2:
        category_name = parts[2].lower()

        categories = await get_categories(
            user_id=user_id,
            category_type=category_type,
            include_default=True
        )

        for cat in categories:
            if category_name in cat.name.lower():
                category = cat
                break

        # Пробуем перевод
        if not category:
            for cat in categories:
                translated = translate_category_name(cat.name, lang).lower()
                if category_name in translated:
                    category = cat
                    break

        if not category:
            for cat in categories:
                if cat.name == "Другое" or cat.name == "Other":
                    category = cat
                    description_parts.append(f"{parts[2]}")
                    break

        if len(parts) > 3:
            description_parts.extend(parts[3:])
    else:
        categories = await get_categories(
            user_id=user_id,
            category_type=category_type,
            include_default=True
        )
        for cat in categories:
            if cat.name == "Другое":
                category = cat
                break

    if not category:
        await message.answer(f"\u274c {t('tx_error_no_category', lang)}")
        return

    description = " ".join(description_parts) if description_parts else None

    try:
        transaction = await create_transaction(
            user_id=user_id,
            transaction_type=transaction_type,
            amount=amount,
            category_id=category.id,
            description=description
        )

        type_emoji = "\U0001f4b0" if transaction_type == TransactionType.INCOME else "\U0001f4b8"
        type_text = t("tx_type_income", lang) if transaction_type == TransactionType.INCOME else t("tx_type_expense", lang)
        sign = "+" if transaction_type == TransactionType.INCOME else "-"
        cat_display = translate_category_name(category.name, lang)

        response = (
            f"\u2705 <b>{t('tx_added', lang)}</b>\n\n"
            f"{type_emoji} <b>{type_text}</b>\n"
            f"\U0001f4b5 {t('tx_amount_label', lang)}: <b>{sign}{float(amount):.2f} \u20bd</b>\n"
            f"{category.emoji} {t('tx_category_label', lang)}: <b>{cat_display}</b>"
        )

        if description:
            response += f"\n\U0001f4dd {t('tx_description_label', lang)}: {description}"

        await message.answer(response)

    except Exception as e:
        from bot.utils.sanitizer import sanitize_exception_message
        safe_error = sanitize_exception_message(e)
        logger.error(f"Ошибка создания транзакции: {safe_error}")
        await message.answer(f"\u274c {t('tx_error_save', lang)}")


## Выбор типа транзакции
@router.callback_query(StateFilter(AddTransactionStates.choosing_type), F.data.startswith("type:"))
async def process_type_selection(callback: CallbackQuery, state: FSMContext, lang: str = "ru") -> None:
    """Обработка выбора типа транзакции."""
    transaction_type = callback.data.split(":")[1]

    await state.update_data(
        transaction_type=transaction_type,
        category_type=CategoryType.EXPENSE if transaction_type == "expense" else CategoryType.INCOME,
        lang=lang
    )

    await state.set_state(AddTransactionStates.entering_amount)

    type_emoji = "\U0001f4b8" if transaction_type == "expense" else "\U0001f4b0"
    type_text = t("tx_type_expense", lang) if transaction_type == "expense" else t("tx_type_income", lang)

    await callback.message.edit_text(
        f"{type_emoji} <b>{type_text}</b>\n\n"
        f"{t('tx_enter_amount', lang)}\n\n"
        f"<i>{t('tx_amount_examples', lang)}</i>",
        reply_markup=get_cancel_keyboard(lang=lang)
    )

    await callback.answer()


## Ввод суммы
@router.message(StateFilter(AddTransactionStates.entering_amount))
async def process_amount_input(message: Message, state: FSMContext, lang: str = "ru") -> None:
    """Обработка ввода суммы."""
    from sqlalchemy import select
    from bot.models import User, get_session
    from datetime import datetime, timezone
    from config import get_settings

    is_valid, amount, error_msg = validate_amount(message.text)

    if not is_valid:
        await message.answer(
            f"{error_msg}\n\n{t('tx_error_enter_valid', lang)}",
            reply_markup=get_cancel_keyboard(lang=lang)
        )
        return

    data = await state.get_data()
    transaction_type = data.get("transaction_type")
    lang = data.get("lang", lang)

    if transaction_type == "expense":
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == message.from_user.id)
            )
            user = result.scalar_one_or_none()

            if user:
                settings = get_settings()

                transaction_limit = user.max_transaction_limit or settings.max_transaction_amount

                if amount > transaction_limit:
                    await message.answer(
                        f"\u26a0\ufe0f {t('limit_warning_transaction', lang, amount=f'{float(amount):,.0f}', limit=f'{transaction_limit:,}')}",
                        parse_mode="HTML"
                    )

                if user.monthly_limit:
                    now = datetime.now(timezone.utc)
                    start_month = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
                    from bot.services.database import get_user_statistics
                    stats = await get_user_statistics(user.id, start_date=start_month)

                    current_spent = sum(float(v) for v in stats.get('expense_by_currency', {}).values())
                    new_total = current_spent + amount

                    if new_total > user.monthly_limit:
                        remaining = user.monthly_limit - current_spent
                        over_limit = new_total - user.monthly_limit

                        await message.answer(
                            f"\U0001f6a8 {t('limit_warning_monthly_exceeded', lang, spent=f'{current_spent:,.0f}', limit=f'{user.monthly_limit:,}', remaining=f'{remaining:,.0f}', over=f'{over_limit:,.0f}')}",
                            parse_mode="HTML"
                        )
                    elif (new_total / user.monthly_limit) >= 0.8:
                        percent = (new_total / user.monthly_limit) * 100
                        remaining = user.monthly_limit - new_total

                        await message.answer(
                            f"\u26a0\ufe0f {t('limit_warning_monthly_approaching', lang, percent=percent, remaining=f'{remaining:,.0f}')}",
                            parse_mode="HTML"
                        )

    await state.update_data(amount=amount)
    await state.set_state(AddTransactionStates.choosing_category)

    data = await state.get_data()
    user_id = data["user_id"]
    category_type = data["category_type"]

    categories = await get_categories(
        user_id=user_id,
        category_type=category_type,
        include_default=True
    )

    categories_list = [(cat.id, cat.name, cat.emoji) for cat in categories]

    type_emoji = "\U0001f4b8" if category_type == CategoryType.EXPENSE else "\U0001f4b0"
    type_text = t("tx_category_of_expense", lang) if category_type == CategoryType.EXPENSE else t("tx_category_of_income", lang)

    await message.answer(
        f"{type_emoji} <b>{t('tx_amount_set', lang, amount=f'{float(amount):.2f}', currency='\u20bd')}</b>\n\n"
        f"{t('tx_choose_category', lang, type=type_text)}",
        reply_markup=get_categories_keyboard(categories_list, data["transaction_type"], lang)
    )


## Выбор категории
@router.callback_query(StateFilter(AddTransactionStates.choosing_category), F.data.startswith("category:"))
async def process_category_selection(callback: CallbackQuery, state: FSMContext, lang: str = "ru") -> None:
    """Обработка выбора категории."""
    data = await state.get_data()
    lang = data.get("lang", lang)
    category_data = callback.data.split(":")[1]

    if category_data == "custom":
        await state.set_state(AddTransactionStates.entering_custom_category)

        type_text = t("tx_category_of_expense", lang) if data["category_type"] == CategoryType.EXPENSE else t("tx_category_of_income", lang)

        await callback.message.edit_text(
            f"\u270f\ufe0f <b>{t('tx_custom_category_title', lang)}</b>\n\n"
            f"{t('tx_custom_category_prompt', lang, type=type_text)}",
            reply_markup=get_cancel_keyboard(lang=lang)
        )
    else:
        category_id = int(category_data)
        category = await get_category_by_id(category_id)

        if not category:
            await callback.answer(f"\u274c {t('cat_not_found', lang)}", show_alert=True)
            return

        await state.update_data(
            category_id=category_id,
            category_name=category.name,
            category_emoji=category.emoji
        )

        await state.set_state(AddTransactionStates.entering_description)

        cat_display = translate_category_name(category.name, lang)

        await callback.message.edit_text(
            f"{category.emoji} <b>{t('tx_category_set', lang, name=cat_display)}</b>\n\n"
            f"{t('tx_enter_description', lang)}",
            reply_markup=get_cancel_keyboard(skip_button=True, lang=lang)
        )

    await callback.answer()


## Ввод пользовательской категории
@router.message(StateFilter(AddTransactionStates.entering_custom_category))
async def process_custom_category_input(message: Message, state: FSMContext, lang: str = "ru") -> None:
    """Обработка ввода пользовательской категории."""
    data = await state.get_data()
    lang = data.get("lang", lang)

    category_name = sanitize_text(message.text, max_length=50)

    is_valid, error_msg = validate_category_name(category_name)
    if not is_valid:
        await message.answer(
            f"{error_msg}\n\n{t('cat_edit_name_prompt', lang)}",
            reply_markup=get_cancel_keyboard(lang=lang)
        )
        return

    try:
        category = await create_custom_category(
            user_id=data["user_id"],
            name=category_name,
            category_type=data["category_type"],
            emoji="\u270f\ufe0f"
        )

        await state.update_data(
            category_id=category.id,
            category_name=category.name,
            category_emoji=category.emoji
        )

        await state.set_state(AddTransactionStates.entering_description)

        await message.answer(
            f"{category.emoji} <b>{t('tx_category_set', lang, name=category.name)}</b>\n\n"
            f"{t('tx_enter_description', lang)}",
            reply_markup=get_cancel_keyboard(skip_button=True, lang=lang)
        )

    except Exception as e:
        from bot.utils.sanitizer import sanitize_exception_message
        safe_error = sanitize_exception_message(e)
        logger.error(f"Ошибка создания категории: {safe_error}")
        await message.answer(
            f"\u274c {t('cat_create_error', lang)}",
            reply_markup=get_cancel_keyboard(lang=lang)
        )


## Ввод описания
@router.message(StateFilter(AddTransactionStates.entering_description))
async def process_description_input(message: Message, state: FSMContext, lang: str = "ru") -> None:
    """Обработка ввода описания."""
    data = await state.get_data()
    lang = data.get("lang", lang)

    description = sanitize_text(message.text, max_length=500)

    is_valid, error_msg = validate_description(description)
    if not is_valid:
        await message.answer(
            f"{error_msg}\n\n{t('edit_description_enter', lang)}",
            reply_markup=get_cancel_keyboard(skip_button=True, lang=lang)
        )
        return

    await state.update_data(description=description)
    await show_confirmation(message, state, lang=lang)


## Пропуск описания
@router.callback_query(StateFilter(AddTransactionStates.entering_description), F.data == "skip")
async def process_skip_description(callback: CallbackQuery, state: FSMContext, lang: str = "ru") -> None:
    """Обработка пропуска описания."""
    data = await state.get_data()
    lang = data.get("lang", lang)

    await state.update_data(description=None)
    await show_confirmation(callback.message, state, edit=True, lang=lang)
    await callback.answer()


## Показ страницы подтверждения
async def show_confirmation(message: Message, state: FSMContext, edit: bool = False, lang: str = "ru") -> None:
    """Показать страницу подтверждения транзакции."""
    await state.set_state(AddTransactionStates.confirmation)

    data = await state.get_data()
    lang = data.get("lang", lang)

    transaction_type = data["transaction_type"]
    amount = data["amount"]
    category_name = data["category_name"]
    category_emoji = data["category_emoji"]
    description = data.get("description")

    type_emoji = "\U0001f4b0" if transaction_type == "income" else "\U0001f4b8"
    type_text = t("tx_type_income", lang) if transaction_type == "income" else t("tx_type_expense", lang)
    sign = "+" if transaction_type == "income" else "-"
    cat_display = translate_category_name(category_name, lang)

    text = (
        f"\U0001f4cb <b>{t('tx_confirmation_title', lang)}</b>\n\n"
        f"{type_emoji} <b>{type_text}</b>\n"
        f"\U0001f4b5 {t('tx_amount_label', lang)}: <b>{sign}{float(amount):.2f} \u20bd</b>\n"
        f"{category_emoji} {t('tx_category_label', lang)}: <b>{cat_display}</b>"
    )

    if description:
        text += f"\n\U0001f4dd {t('tx_description_label', lang)}: {description}"

    text += f"\n\n<i>{t('tx_confirm_correct', lang)}</i>"

    if edit:
        await message.edit_text(text, reply_markup=get_confirmation_keyboard(lang))
    else:
        await message.answer(text, reply_markup=get_confirmation_keyboard(lang))


## Подтверждение транзакции
@router.callback_query(StateFilter(AddTransactionStates.confirmation), F.data.startswith("confirm:"))
async def process_confirmation(callback: CallbackQuery, state: FSMContext, lang: str = "ru") -> None:
    """Обработка подтверждения или отмены."""
    data = await state.get_data()
    lang = data.get("lang", lang)
    action = callback.data.split(":")[1]

    if action == "no":
        await state.clear()
        await callback.message.edit_text(f"\u274c {t('tx_cancelled', lang)}")
        await callback.answer()
        return

    try:
        transaction_type_str = data["transaction_type"]
        transaction_type = TransactionType.INCOME if transaction_type_str == "income" else TransactionType.EXPENSE

        transaction = await create_transaction(
            user_id=data["user_id"],
            transaction_type=transaction_type,
            amount=data["amount"],
            category_id=data["category_id"],
            description=data.get("description")
        )

        type_emoji = "\U0001f4b0" if transaction_type == TransactionType.INCOME else "\U0001f4b8"
        sign = "+" if transaction_type == TransactionType.INCOME else "-"
        cat_display = translate_category_name(data['category_name'], lang)

        await callback.message.edit_text(
            f"\u2705 <b>{t('tx_saved', lang)}</b>\n\n"
            f"{type_emoji} {sign}{float(data['amount']):.2f} \u20bd\n"
            f"{data['category_emoji']} {cat_display}",
            reply_markup=get_edit_transaction_button(transaction.id, lang)
        )

        await state.clear()

    except Exception as e:
        from bot.utils.sanitizer import sanitize_exception_message
        safe_error = sanitize_exception_message(e)
        logger.error(f"Ошибка сохранения транзакции: {safe_error}")
        await callback.message.edit_text(f"\u274c {t('tx_error_save', lang)}")
        await state.clear()

    await callback.answer()


## Отмена добавления транзакции
@router.callback_query(StateFilter("*"), F.data == "cancel")
async def process_cancel(callback: CallbackQuery, state: FSMContext, lang: str = "ru") -> None:
    """Обработка отмены."""
    await state.clear()
    await callback.message.edit_text(f"\u274c {t('tx_operation_cancelled', lang)}")
    await callback.answer()


## Обработчик Reply кнопки "Добавить"
@router.message(F.text.in_({"\u2795 Добавить", "\u2795 Add"}))
async def handle_add_button(message: Message, state: FSMContext, lang: str = "ru") -> None:
    """Начать добавление транзакции (Reply кнопка)."""
    user = await get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )

    logger.info(f"Пользователь {user.id} начал добавление транзакции через Reply кнопку")

    await state.set_state(AddTransactionStates.choosing_type)
    await state.update_data(user_id=user.id, lang=lang)

    await message.answer(
        f"\U0001f4b0 <b>{t('tx_add_title', lang)}</b>\n\n"
        f"{t('tx_choose_type', lang)}",
        reply_markup=get_transaction_type_keyboard(lang)
    )
