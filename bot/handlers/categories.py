"""
Обработчики управления категориями.

Содержит handlers для просмотра, добавления, редактирования и удаления категорий.
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

router = Router(name="categories")


## Главное меню управления категориями
@router.message(Command("categories"))
async def cmd_categories(message: Message) -> None:
    """
    Обработчик команды /categories.
    
    Показывает главное меню управления категориями.
    
    :param message: Объект сообщения от пользователя
    :return: None
    """
    user = await get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    
    logger.info(f"Пользователь {user.telegram_id} открыл управление категориями")
    
    text = (
        "🏷️ <b>Управление категориями</b>\n\n"
        "Здесь ты можешь просматривать свои категории, "
        "создавать новые и редактировать существующие.\n\n"
        "💡 <b>Совет:</b> Создавай категории для точного учёта расходов!"
    )
    
    await message.answer(
        text,
        reply_markup=get_category_management_menu(),
        parse_mode="HTML"
    )


## Просмотр пользовательских категорий
@router.callback_query(F.data == "cat:view_my")
async def view_user_categories(callback: CallbackQuery) -> None:
    """
    Показать список пользовательских категорий.
    
    :param callback: Callback query от inline-кнопки
    :return: None
    """
    user = await get_or_create_user(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        last_name=callback.from_user.last_name
    )
    
    categories = await get_categories(user_id=user.id, include_default=True)
    
    if not categories:
        await callback.answer("🚫 У тебя пока нет категорий", show_alert=True)
        return
    
    # Формируем данные для клавиатуры
    categories_data = [
        (cat.id, cat.name, cat.emoji, cat.is_default)
        for cat in categories
    ]
    
    # Разделяем на пользовательские и предустановленные
    custom_cats = [c for c in categories if not c.is_default]
    default_cats = [c for c in categories if c.is_default]
    
    text = "📋 <b>Твои категории</b>\n\n"
    
    if custom_cats:
        text += "✏️ <b>Пользовательские:</b>\n"
        for cat in custom_cats:
            text += f"• {cat.emoji} {cat.name}\n"
        text += "\n"
    else:
        text += "🚫 У тебя пока нет пользовательских категорий\n\n"
    
    text += f"📌 Предустановленных категорий: {len(default_cats)}\n\n"
    text += "💡 Выбери категорию для редактирования"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_user_categories_keyboard(categories_data),
        parse_mode="HTML"
    )
    await callback.answer()


## Начало добавления категории
@router.callback_query(F.data == "cat:add")
async def start_add_category(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Начать процесс добавления новой категории.
    
    :param callback: Callback query от inline-кнопки
    :param state: Состояние FSM
    :return: None
    """
    await state.set_state(CategoryStates.choosing_type)
    
    text = (
        "➕ <b>Добавление категории</b>\n\n"
        "Сначала выбери тип категории:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_category_type_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


## Выбор типа новой категории
@router.callback_query(CategoryStates.choosing_type, F.data.startswith("cattype:"))
async def choose_category_type(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обработать выбор типа категории.
    
    :param callback: Callback query от inline-кнопки
    :param state: Состояние FSM
    :return: None
    """
    category_type = callback.data.split(":")[1]
    await state.update_data(category_type=category_type)
    await state.set_state(CategoryStates.entering_name)
    
    type_emoji = "💰" if category_type == "income" else "💸"
    type_name = "доходов" if category_type == "income" else "расходов"
    
    text = (
        f"{type_emoji} <b>Категория {type_name}</b>\n\n"
        "Введи название новой категории:\n\n"
        "📝 <i>Например: Подписки, Хобби, Образование</i>"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


## Ввод названия категории
@router.message(CategoryStates.entering_name, F.text)
async def enter_category_name(message: Message, state: FSMContext) -> None:
    """
    Обработать ввод названия категории.
    
    :param message: Объект сообщения от пользователя
    :param state: Состояние FSM
    :return: None
    """
    name = message.text.strip()
    
    if len(name) > 100:
        await message.answer(
            "❌ Название слишком длинное. Максимум 100 символов.\n\n"
            "Попробуй еще раз:",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    if len(name) < 2:
        await message.answer(
            "❌ Название слишком короткое. Минимум 2 символа.\n\n"
            "Попробуй еще раз:",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    await state.update_data(name=name)
    await state.set_state(CategoryStates.entering_emoji)
    
    text = (
        f"✅ Название: <b>{name}</b>\n\n"
        "Теперь введи эмодзи для категории:\n\n"
        "🎨 <i>Например: 📱 💻 🎮 📚 ✈️</i>\n\n"
        "💡 Можешь скопировать любой эмодзи"
    )
    
    await message.answer(
        text,
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )


## Ввод эмодзи категории
@router.message(CategoryStates.entering_emoji, F.text)
async def enter_category_emoji(message: Message, state: FSMContext) -> None:
    """
    Обработать ввод эмодзи категории.
    
    :param message: Объект сообщения от пользователя
    :param state: Состояние FSM
    :return: None
    """
    emoji = message.text.strip()
    
    if len(emoji) > 10:
        emoji = emoji[:10]
    
    if not emoji:
        emoji = "✏️"
    
    await state.update_data(emoji=emoji)
    await state.set_state(CategoryStates.confirming)
    
    data = await state.get_data()
    name = data.get('name')
    category_type = data.get('category_type')
    
    type_emoji = "💰" if category_type == "income" else "💸"
    type_name = "Доход" if category_type == "income" else "Расход"
    
    text = (
        f"✅ <b>Подтверди создание категории</b>\n\n"
        f"Тип: {type_emoji} {type_name}\n"
        f"Название: {name}\n"
        f"Эмодзи: {emoji}\n\n"
        "Всё верно?"
    )
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Создать", callback_data="catconfirm:yes"),
        InlineKeyboardButton(text="❌ Отменить", callback_data="cat:cancel")
    )
    
    await message.answer(
        text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )


## Подтверждение создания категории
@router.callback_query(CategoryStates.confirming, F.data == "catconfirm:yes")
async def confirm_create_category(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Подтвердить и создать категорию.
    
    :param callback: Callback query от inline-кнопки
    :param state: Состояние FSM
    :return: None
    """
    user = await get_or_create_user(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        last_name=callback.from_user.last_name
    )
    
    data = await state.get_data()
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
        
        logger.success(f"Создана категория {category.id} для пользователя {user.telegram_id}")
        
        text = (
            f"✅ <b>Категория создана!</b>\n\n"
            f"{emoji} <b>{name}</b>\n\n"
            "Теперь ты можешь использовать её при добавлении транзакций."
        )
        
        await callback.message.edit_text(
            text,
            reply_markup=get_category_management_menu(),
            parse_mode="HTML"
        )
        
    except Exception as e:
        from bot.utils.sanitizer import sanitize_exception_message
        safe_error = sanitize_exception_message(e)
        logger.error(f"Ошибка создания категории: {safe_error}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при создании категории.\n\n"
            "Попробуй еще раз.",
            reply_markup=get_category_management_menu()
        )
    
    await state.clear()
    await callback.answer()


## Просмотр/редактирование категории
@router.callback_query(F.data.startswith("cat:edit:"))
async def view_category_details(callback: CallbackQuery) -> None:
    """
    Показать детали категории и меню редактирования.
    
    :param callback: Callback query от inline-кнопки
    :return: None
    """
    category_id = int(callback.data.split(":")[2])
    
    category = await get_category_by_id(category_id)
    
    if not category:
        await callback.answer("❌ Категория не найдена", show_alert=True)
        return
    
    user = await get_or_create_user(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        last_name=callback.from_user.last_name
    )
    
    # Подсчитываем транзакции
    trans_count = await count_category_transactions(category_id, user.id)
    
    type_name = "💰 Доход" if category.type == CategoryType.INCOME else "💸 Расход"
    status = "📌 Предустановленная" if category.is_default else "✏️ Пользовательская"
    
    text = (
        f"🏷️ <b>{category.emoji} {category.name}</b>\n\n"
        f"Тип: {type_name}\n"
        f"Статус: {status}\n"
        f"Транзакций: {trans_count}\n\n"
    )
    
    if category.is_default:
        text += "🔒 Предустановленные категории нельзя изменить или удалить"
    else:
        text += "Выбери действие:"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_category_edit_menu(category.is_default),
        parse_mode="HTML"
    )
    await callback.answer()


## Редактирование названия
@router.callback_query(F.data == "catedit:name")
async def start_edit_name(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Начать редактирование названия категории.
    
    :param callback: Callback query от inline-кнопки
    :param state: Состояние FSM
    :return: None
    """
    # Извлекаем ID категории из предыдущего сообщения
    message_text = callback.message.text
    lines = message_text.split('\n')
    category_name_line = lines[0].replace('🏷️ ', '').strip()
    
    # Ищем категорию по имени (временное решение)
    user = await get_or_create_user(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        last_name=callback.from_user.last_name
    )
    
    categories = await get_categories(user_id=user.id, include_default=False)
    
    # Находим категорию
    category = None
    for cat in categories:
        if f"{cat.emoji} {cat.name}" in category_name_line:
            category = cat
            break
    
    if not category:
        await callback.answer("❌ Категория не найдена", show_alert=True)
        return
    
    await state.update_data(editing_category_id=category.id, editing_field='name')
    await state.set_state(CategoryStates.editing_category)
    
    text = (
        f"✏️ <b>Изменение названия</b>\n\n"
        f"Текущее название: <b>{category.name}</b>\n\n"
        "Введи новое название:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


## Обработка редактирования
@router.message(CategoryStates.editing_category, F.text)
async def process_category_edit(message: Message, state: FSMContext) -> None:
    """
    Обработать редактирование категории.
    
    :param message: Объект сообщения от пользователя
    :param state: Состояние FSM
    :return: None
    """
    data = await state.get_data()
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
                "❌ Название должно быть от 2 до 100 символов.\n\n"
                "Попробуй еще раз:",
                reply_markup=get_cancel_keyboard()
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
            f"✅ <b>Категория обновлена!</b>\n\n"
            f"{updated.emoji} <b>{updated.name}</b>"
        )
        
        await message.answer(
            text,
            reply_markup=get_category_management_menu(),
            parse_mode="HTML"
        )
        logger.success(f"Категория {category_id} обновлена пользователем {user.telegram_id}")
    else:
        await message.answer(
            "❌ Не удалось обновить категорию",
            reply_markup=get_category_management_menu()
        )


## Редактирование эмодзи
@router.callback_query(F.data == "catedit:emoji")
async def start_edit_emoji(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Начать редактирование эмодзи категории.
    
    :param callback: Callback query от inline-кнопки
    :param state: Состояние FSM
    :return: None
    """
    message_text = callback.message.text
    lines = message_text.split('\n')
    category_name_line = lines[0].replace('🏷️ ', '').strip()
    
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
    
    if not category:
        await callback.answer("❌ Категория не найдена", show_alert=True)
        return
    
    await state.update_data(editing_category_id=category.id, editing_field='emoji')
    await state.set_state(CategoryStates.editing_category)
    
    text = (
        f"🎨 <b>Изменение эмодзи</b>\n\n"
        f"Текущий эмодзи: {category.emoji}\n\n"
        "Введи новый эмодзи:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


## Удаление категории
@router.callback_query(F.data == "catedit:delete")
async def confirm_delete_category(callback: CallbackQuery) -> None:
    """
    Запросить подтверждение удаления категории.
    
    :param callback: Callback query от inline-кнопки
    :return: None
    """
    message_text = callback.message.text
    lines = message_text.split('\n')
    category_name_line = lines[0].replace('🏷️ ', '').strip()
    
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
    
    if not category:
        await callback.answer("❌ Категория не найдена", show_alert=True)
        return
    
    trans_count = await count_category_transactions(category.id, user.id)
    
    text = (
        f"⚠️ <b>Удаление категории</b>\n\n"
        f"Категория: {category.emoji} {category.name}\n"
        f"Транзакций: {trans_count}\n\n"
    )
    
    if trans_count > 0:
        text += (
            "⚠️ <b>Внимание!</b> У этой категории есть транзакции.\n"
            "При удалении категории все связанные транзакции также будут удалены.\n\n"
            "Ты уверен?"
        )
    else:
        text += "Ты уверен, что хочешь удалить эту категорию?"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_delete_confirmation_keyboard(category.id),
        parse_mode="HTML"
    )
    await callback.answer()


## Подтверждение удаления
@router.callback_query(F.data.startswith("catdel:confirm:"))
async def delete_category_confirmed(callback: CallbackQuery) -> None:
    """
    Удалить категорию после подтверждения.
    
    :param callback: Callback query от inline-кнопки
    :return: None
    """
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
            "✅ <b>Категория удалена</b>\n\n"
            "Категория и все связанные с ней транзакции удалены."
        )
        logger.success(f"Категория {category_id} удалена пользователем {user.telegram_id}")
    else:
        text = "❌ Не удалось удалить категорию"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_category_management_menu(),
        parse_mode="HTML"
    )
    await callback.answer()


## Отмена операции
@router.callback_query(F.data == "cat:cancel")
async def cancel_category_operation(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Отменить текущую операцию с категорией.
    
    :param callback: Callback query от inline-кнопки
    :param state: Состояние FSM
    :return: None
    """
    await state.clear()
    
    text = (
        "❌ <b>Операция отменена</b>\n\n"
        "Выбери другое действие:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_category_management_menu(),
        parse_mode="HTML"
    )
    await callback.answer()


## Возврат в меню категорий
@router.callback_query(F.data == "cat:back")
async def back_to_categories(callback: CallbackQuery) -> None:
    """
    Вернуться в главное меню категорий.
    
    :param callback: Callback query от inline-кнопки
    :return: None
    """
    text = (
        "🏷️ <b>Управление категориями</b>\n\n"
        "Здесь ты можешь просматривать свои категории, "
        "создавать новые и редактировать существующие.\n\n"
        "💡 <b>Совет:</b> Создавай категории для точного учёта расходов!"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_category_management_menu(),
        parse_mode="HTML"
    )
    await callback.answer()


## Возврат в главное меню
@router.callback_query(F.data == "back_to_menu")
async def back_to_main_menu(callback: CallbackQuery) -> None:
    """
    Вернуться в главное меню бота.
    
    :param callback: Callback query от inline-кнопки
    :return: None
    """
    from bot.keyboards.view_keyboards import get_main_menu_keyboard
    
    await callback.message.edit_text(
        "📋 <b>Главное меню</b>\n\n"
        "Выбери действие:",
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


## Обработчик Reply кнопки "🏷️ Категории"
@router.message(F.text == "🏷️ Категории")
async def handle_categories_button(message: Message) -> None:
    """
    Показать меню управления категориями (Reply кнопка).
    
    :param message: Сообщение от пользователя
    :return: None
    """
    user = await get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )
    
    logger.info(f"Пользователь {user.id} открыл управление категориями через Reply кнопку")
    
    text = (
        "🏷️ <b>Управление категориями</b>\n\n"
        "Здесь ты можешь просматривать свои категории, "
        "создавать новые и редактировать существующие.\n\n"
        "💡 <b>Совет:</b> Создавай категории для точного учёта расходов!"
    )
    
    await message.answer(
        text,
        reply_markup=get_category_management_menu(),
        parse_mode="HTML"
    )
