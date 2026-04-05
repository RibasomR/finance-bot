"""
Обработчики управления категориями.

Поддержка мультиязычности через locales.
"""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from loguru import logger

from bot.states.category_states import CategoryStates
from bot.keyboards.category_keyboards import (
    get_category_management_menu,
    get_category_type_keyboard,
    get_user_categories_keyboard,
    get_category_edit_menu,
    get_delete_confirmation_keyboard,
    get_cancel_keyboard
)
from bot.services.database import (
    get_or_create_user,
    get_categories,
    get_category_by_id,
    create_custom_category,
    update_category,
    delete_category,
    count_category_transactions
)
from bot.models import CategoryType
from bot.locales import t, translate_category_name

router = Router(name="categories")


def _cat_menu_text(lang: str) -> str:
    """Текст меню категорий."""
    return (
        f"\U0001f3f7\ufe0f <b>{t('cat_management_title', lang)}</b>\n\n"
        f"{t('cat_management_subtitle', lang)}"
    )


## Команда /categories
@router.message(Command("categories"))
async def cmd_categories(message: Message, lang: str = "ru") -> None:
    """Главное меню категорий."""
    await get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )

    await message.answer(
        _cat_menu_text(lang),
        reply_markup=get_category_management_menu(lang),
        parse_mode="HTML"
    )


## Просмотр категорий
@router.callback_query(F.data == "cat:view_my")
async def view_user_categories(callback: CallbackQuery, lang: str = "ru") -> None:
    """Показать категории пользователя."""
    user = await get_or_create_user(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        last_name=callback.from_user.last_name
    )

    categories = await get_categories(user_id=user.id, include_default=True)

    if not categories:
        await callback.answer(f"\U0001f6ab {t('cat_no_categories', lang)}", show_alert=True)
        return

    categories_data = [
        (cat.id, cat.name, cat.emoji, cat.is_default)
        for cat in categories
    ]

    custom_cats = [c for c in categories if not c.is_default]
    default_cats = [c for c in categories if c.is_default]

    text = f"\U0001f4cb <b>{t('cat_title_list', lang)}</b>\n\n"

    if custom_cats:
        text += f"\u270f\ufe0f <b>{t('cat_custom_label', lang)}</b>\n"
        for cat in custom_cats:
            text += f"- {cat.emoji} {cat.name}\n"
        text += "\n"
    else:
        text += f"\U0001f6ab {t('cat_no_custom', lang)}\n\n"

    text += f"\U0001f4cc {t('cat_default_count', lang, count=len(default_cats))}\n\n"
    text += f"\U0001f4a1 {t('cat_choose_to_edit', lang)}"

    await callback.message.edit_text(
        text,
        reply_markup=get_user_categories_keyboard(categories_data, lang=lang),
        parse_mode="HTML"
    )
    await callback.answer()


## Добавление категории
@router.callback_query(F.data == "cat:add")
async def start_add_category(callback: CallbackQuery, state: FSMContext, lang: str = "ru") -> None:
    """Начать добавление категории."""
    await state.set_state(CategoryStates.choosing_type)
    await state.update_data(lang=lang)

    text = (
        f"\u2795 <b>{t('cat_add_title', lang)}</b>\n\n"
        f"{t('cat_add_choose_type', lang)}"
    )

    await callback.message.edit_text(
        text,
        reply_markup=get_category_type_keyboard(lang),
        parse_mode="HTML"
    )
    await callback.answer()


## Выбор типа
@router.callback_query(CategoryStates.choosing_type, F.data.startswith("cattype:"))
async def choose_category_type(callback: CallbackQuery, state: FSMContext, lang: str = "ru") -> None:
    """Обработать выбор типа категории."""
    data = await state.get_data()
    lang = data.get("lang", lang)
    category_type = callback.data.split(":")[1]
    await state.update_data(category_type=category_type)
    await state.set_state(CategoryStates.entering_name)

    type_emoji = "\U0001f4b0" if category_type == "income" else "\U0001f4b8"
    type_name = t("cat_add_type_income", lang) if category_type == "income" else t("cat_add_type_expense", lang)

    text = (
        f"{type_emoji} <b>{t('cat_add_title', lang)} ({type_name})</b>\n\n"
        f"{t('cat_add_name_prompt', lang)}"
    )

    await callback.message.edit_text(
        text,
        reply_markup=get_cancel_keyboard(lang),
        parse_mode="HTML"
    )
    await callback.answer()


## Ввод названия
@router.message(CategoryStates.entering_name, F.text)
async def enter_category_name(message: Message, state: FSMContext, lang: str = "ru") -> None:
    """Обработать ввод названия."""
    data = await state.get_data()
    lang = data.get("lang", lang)
    name = message.text.strip()

    if len(name) > 100:
        await message.answer(
            f"\u274c {t('cat_add_name_too_long', lang)}",
            reply_markup=get_cancel_keyboard(lang)
        )
        return

    if len(name) < 2:
        await message.answer(
            f"\u274c {t('cat_add_name_too_short', lang)}",
            reply_markup=get_cancel_keyboard(lang)
        )
        return

    await state.update_data(name=name)
    await state.set_state(CategoryStates.entering_emoji)

    text = (
        f"\u2705 {t('cat_add_name_label', lang)} <b>{name}</b>\n\n"
        f"{t('cat_add_emoji_prompt', lang)}"
    )

    await message.answer(
        text,
        reply_markup=get_cancel_keyboard(lang),
        parse_mode="HTML"
    )


## Ввод эмодзи
@router.message(CategoryStates.entering_emoji, F.text)
async def enter_category_emoji(message: Message, state: FSMContext, lang: str = "ru") -> None:
    """Обработать ввод эмодзи."""
    data = await state.get_data()
    lang = data.get("lang", lang)
    emoji = message.text.strip()

    if len(emoji) > 10:
        emoji = emoji[:10]

    if not emoji:
        emoji = "\u270f\ufe0f"

    await state.update_data(emoji=emoji)
    await state.set_state(CategoryStates.confirming)

    name = data.get('name')
    category_type = data.get('category_type')

    type_emoji = "\U0001f4b0" if category_type == "income" else "\U0001f4b8"
    type_name = t("tx_type_income", lang) if category_type == "income" else t("tx_type_expense", lang)

    text = (
        f"\u2705 <b>{t('cat_add_confirm', lang)}</b>\n\n"
        f"{t('cat_add_type_label', lang)} {type_emoji} {type_name}\n"
        f"{t('cat_add_name_label', lang)} {name}\n"
        f"{t('cat_add_emoji_label', lang)} {emoji}\n\n"
        f"{t('cat_add_confirm_question', lang)}"
    )

    from aiogram.types import InlineKeyboardButton
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=f"\u2705 {t('create', lang)}", callback_data="catconfirm:yes"),
        InlineKeyboardButton(text=f"\u274c {t('cancel', lang)}", callback_data="cat:cancel")
    )

    await message.answer(
        text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )


## Подтверждение создания
@router.callback_query(CategoryStates.confirming, F.data == "catconfirm:yes")
async def confirm_create_category(callback: CallbackQuery, state: FSMContext, lang: str = "ru") -> None:
    """Подтвердить и создать категорию."""
    data = await state.get_data()
    lang = data.get("lang", lang)
    user = await get_or_create_user(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        last_name=callback.from_user.last_name
    )

    name = data.get('name')
    emoji = data.get('emoji')
    category_type_str = data.get('category_type')

    category_type = CategoryType.INCOME if category_type_str == "income" else CategoryType.EXPENSE

    try:
        category = await create_custom_category(
            user_id=user.id,
            name=name,
            category_type=category_type,
            emoji=emoji
        )

        text = (
            f"\u2705 <b>{t('cat_created', lang)}</b>\n\n"
            f"{emoji} <b>{name}</b>\n\n"
            f"{t('cat_created_detail', lang)}"
        )

        await callback.message.edit_text(
            text,
            reply_markup=get_category_management_menu(lang),
            parse_mode="HTML"
        )

    except Exception as e:
        from bot.utils.sanitizer import sanitize_exception_message
        safe_error = sanitize_exception_message(e)
        logger.error(f"Ошибка создания категории: {safe_error}")
        await callback.message.edit_text(
            f"\u274c {t('cat_create_error', lang)}",
            reply_markup=get_category_management_menu(lang)
        )

    await state.clear()
    await callback.answer()


## Просмотр категории
@router.callback_query(F.data.startswith("cat:edit:"))
async def view_category_details(callback: CallbackQuery, lang: str = "ru") -> None:
    """Показать детали категории."""
    category_id = int(callback.data.split(":")[2])

    category = await get_category_by_id(category_id)

    if not category:
        await callback.answer(f"\u274c {t('cat_not_found', lang)}", show_alert=True)
        return

    user = await get_or_create_user(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        last_name=callback.from_user.last_name
    )

    trans_count = await count_category_transactions(category_id, user.id)

    type_name = f"\U0001f4b0 {t('cat_detail_type_income', lang)}" if category.type == CategoryType.INCOME else f"\U0001f4b8 {t('cat_detail_type_expense', lang)}"
    status = f"\U0001f4cc {t('cat_detail_status_default', lang)}" if category.is_default else f"\u270f\ufe0f {t('cat_detail_status_custom', lang)}"
    cat_display = translate_category_name(category.name, lang)

    text = (
        f"\U0001f3f7\ufe0f <b>{category.emoji} {cat_display}</b>\n\n"
        f"{type_name}\n"
        f"{status}\n"
        f"{t('cat_detail_transactions', lang, count=trans_count)}\n\n"
    )

    if category.is_default:
        text += f"\U0001f512 {t('cat_detail_locked', lang)}"
    else:
        text += t("cat_detail_choose_action", lang)

    await callback.message.edit_text(
        text,
        reply_markup=get_category_edit_menu(category.is_default, lang),
        parse_mode="HTML"
    )
    await callback.answer()


## Редактирование названия
@router.callback_query(F.data == "catedit:name")
async def start_edit_name(callback: CallbackQuery, state: FSMContext, lang: str = "ru") -> None:
    """Начать редактирование названия."""
    message_text = callback.message.text
    lines = message_text.split('\n')
    category_name_line = lines[0].replace('\U0001f3f7\ufe0f ', '').strip()

    user = await get_or_create_user(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        last_name=callback.from_user.last_name
    )

    categories = await get_categories(user_id=user.id, include_default=False)

    category = None
    for cat in categories:
        if f"{cat.emoji} {cat.name}" in category_name_line:
            category = cat
            break
        translated = translate_category_name(cat.name, lang)
        if f"{cat.emoji} {translated}" in category_name_line:
            category = cat
            break

    if not category:
        await callback.answer(f"\u274c {t('cat_not_found', lang)}", show_alert=True)
        return

    await state.update_data(editing_category_id=category.id, editing_field='name', lang=lang)
    await state.set_state(CategoryStates.editing_category)

    text = (
        f"\u270f\ufe0f <b>{t('cat_edit_name_title', lang)}</b>\n\n"
        f"{t('cat_edit_name_current', lang, name=category.name)}\n\n"
        f"{t('cat_edit_name_prompt', lang)}"
    )

    await callback.message.edit_text(
        text,
        reply_markup=get_cancel_keyboard(lang),
        parse_mode="HTML"
    )
    await callback.answer()


## Обработка редактирования
@router.message(CategoryStates.editing_category, F.text)
async def process_category_edit(message: Message, state: FSMContext, lang: str = "ru") -> None:
    """Обработать редактирование категории."""
    data = await state.get_data()
    lang = data.get("lang", lang)
    category_id = data.get('editing_category_id')
    field = data.get('editing_field')
    new_value = message.text.strip()

    user = await get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )

    if field == 'name':
        if len(new_value) > 100 or len(new_value) < 2:
            await message.answer(
                f"\u274c {t('cat_edit_name_error', lang)}",
                reply_markup=get_cancel_keyboard(lang)
            )
            return

        updated = await update_category(category_id, user.id, name=new_value)
    elif field == 'emoji':
        if len(new_value) > 10:
            new_value = new_value[:10]

        updated = await update_category(category_id, user.id, emoji=new_value)
    else:
        updated = None

    await state.clear()

    if updated:
        text = (
            f"\u2705 <b>{t('cat_updated', lang)}</b>\n\n"
            f"{updated.emoji} <b>{updated.name}</b>"
        )

        await message.answer(
            text,
            reply_markup=get_category_management_menu(lang),
            parse_mode="HTML"
        )
    else:
        await message.answer(
            f"\u274c {t('cat_update_error', lang)}",
            reply_markup=get_category_management_menu(lang)
        )


## Редактирование эмодзи
@router.callback_query(F.data == "catedit:emoji")
async def start_edit_emoji(callback: CallbackQuery, state: FSMContext, lang: str = "ru") -> None:
    """Начать редактирование эмодзи."""
    message_text = callback.message.text
    lines = message_text.split('\n')
    category_name_line = lines[0].replace('\U0001f3f7\ufe0f ', '').strip()

    user = await get_or_create_user(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        last_name=callback.from_user.last_name
    )

    categories = await get_categories(user_id=user.id, include_default=False)

    category = None
    for cat in categories:
        if f"{cat.emoji} {cat.name}" in category_name_line:
            category = cat
            break
        translated = translate_category_name(cat.name, lang)
        if f"{cat.emoji} {translated}" in category_name_line:
            category = cat
            break

    if not category:
        await callback.answer(f"\u274c {t('cat_not_found', lang)}", show_alert=True)
        return

    await state.update_data(editing_category_id=category.id, editing_field='emoji', lang=lang)
    await state.set_state(CategoryStates.editing_category)

    text = (
        f"\U0001f3a8 <b>{t('cat_edit_emoji_title', lang)}</b>\n\n"
        f"{t('cat_edit_emoji_current', lang, emoji=category.emoji)}\n\n"
        f"{t('cat_edit_emoji_prompt', lang)}"
    )

    await callback.message.edit_text(
        text,
        reply_markup=get_cancel_keyboard(lang),
        parse_mode="HTML"
    )
    await callback.answer()


## Удаление категории
@router.callback_query(F.data == "catedit:delete")
async def confirm_delete_category(callback: CallbackQuery, lang: str = "ru") -> None:
    """Запросить подтверждение удаления."""
    message_text = callback.message.text
    lines = message_text.split('\n')
    category_name_line = lines[0].replace('\U0001f3f7\ufe0f ', '').strip()

    user = await get_or_create_user(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        last_name=callback.from_user.last_name
    )

    categories = await get_categories(user_id=user.id, include_default=False)

    category = None
    for cat in categories:
        if f"{cat.emoji} {cat.name}" in category_name_line:
            category = cat
            break
        translated = translate_category_name(cat.name, lang)
        if f"{cat.emoji} {translated}" in category_name_line:
            category = cat
            break

    if not category:
        await callback.answer(f"\u274c {t('cat_not_found', lang)}", show_alert=True)
        return

    trans_count = await count_category_transactions(category.id, user.id)

    text = (
        f"\u26a0\ufe0f <b>{t('cat_delete_title', lang)}</b>\n\n"
        f"{t('tx_category_label', lang)}: {category.emoji} {category.name}\n"
        f"{t('cat_detail_transactions', lang, count=trans_count)}\n\n"
    )

    if trans_count > 0:
        text += t("cat_delete_has_transactions", lang)
    else:
        text += t("cat_delete_confirm", lang)

    await callback.message.edit_text(
        text,
        reply_markup=get_delete_confirmation_keyboard(category.id, lang),
        parse_mode="HTML"
    )
    await callback.answer()


## Подтверждение удаления
@router.callback_query(F.data.startswith("catdel:confirm:"))
async def delete_category_confirmed(callback: CallbackQuery, lang: str = "ru") -> None:
    """Удалить категорию."""
    category_id = int(callback.data.split(":")[2])

    user = await get_or_create_user(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        last_name=callback.from_user.last_name
    )

    success = await delete_category(category_id, user.id)

    if success:
        text = (
            f"\u2705 <b>{t('cat_deleted', lang)}</b>\n\n"
            f"{t('cat_deleted_detail', lang)}"
        )
    else:
        text = f"\u274c {t('cat_delete_error', lang)}"

    await callback.message.edit_text(
        text,
        reply_markup=get_category_management_menu(lang),
        parse_mode="HTML"
    )
    await callback.answer()


## Отмена
@router.callback_query(F.data == "cat:cancel")
async def cancel_category_operation(callback: CallbackQuery, state: FSMContext, lang: str = "ru") -> None:
    """Отменить операцию."""
    await state.clear()

    text = (
        f"\u274c <b>{t('cat_operation_cancelled', lang)}</b>\n\n"
        f"{t('cat_cancelled_subtitle', lang)}"
    )

    await callback.message.edit_text(
        text,
        reply_markup=get_category_management_menu(lang),
        parse_mode="HTML"
    )
    await callback.answer()


## Возврат в меню категорий
@router.callback_query(F.data == "cat:back")
async def back_to_categories(callback: CallbackQuery, lang: str = "ru") -> None:
    """Вернуться в меню категорий."""
    await callback.message.edit_text(
        _cat_menu_text(lang),
        reply_markup=get_category_management_menu(lang),
        parse_mode="HTML"
    )
    await callback.answer()


## Возврат в главное меню
@router.callback_query(F.data == "back_to_menu")
async def back_to_main_menu(callback: CallbackQuery, lang: str = "ru") -> None:
    """Вернуться в главное меню."""
    from bot.keyboards.view_keyboards import get_main_menu_keyboard

    await callback.message.edit_text(
        f"\U0001f4cb <b>{t('main_menu_title', lang)}</b>\n\n"
        f"{t('main_menu_action', lang)}",
        reply_markup=get_main_menu_keyboard(lang),
        parse_mode="HTML"
    )
    await callback.answer()


## Reply кнопка "Категории"
@router.message(F.text.in_({"\U0001f3f7\ufe0f Категории", "\U0001f3f7\ufe0f Categories"}))
async def handle_categories_button(message: Message, lang: str = "ru") -> None:
    """Показать меню категорий (Reply кнопка)."""
    await get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )

    await message.answer(
        _cat_menu_text(lang),
        reply_markup=get_category_management_menu(lang),
        parse_mode="HTML"
    )
