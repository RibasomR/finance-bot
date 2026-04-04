"""
Клавиатуры для управления категориями.

Functions:
    get_category_management_menu: Главное меню управления категориями
    get_category_type_keyboard: Клавиатура выбора типа категории
    get_user_categories_keyboard: Клавиатура со списком пользовательских категорий
    get_category_edit_menu: Меню редактирования категории
"""

from typing import List
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


## Главное меню управления категориями
def get_category_management_menu() -> InlineKeyboardMarkup:
    """
    Создает главное меню управления категориями.
    
    Returns:
        InlineKeyboardMarkup: Клавиатура с основными действиями
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📋 Мои категории", callback_data="cat:view_my")
    )
    builder.row(
        InlineKeyboardButton(text="➕ Добавить категорию", callback_data="cat:add")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_menu")
    )
    return builder.as_markup()


## Клавиатура выбора типа категории
def get_category_type_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для выбора типа категории.
    
    Returns:
        InlineKeyboardMarkup: Клавиатура с типами категорий
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="💰 Доход", callback_data="cattype:income"),
        InlineKeyboardButton(text="💸 Расход", callback_data="cattype:expense")
    )
    builder.row(
        InlineKeyboardButton(text="❌ Отмена", callback_data="cat:cancel")
    )
    return builder.as_markup()


## Клавиатура с пользовательскими категориями
def get_user_categories_keyboard(
    categories: List[tuple],
    show_default: bool = False
) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру со списком категорий пользователя.
    
    Args:
        categories: Список кортежей (id, name, emoji, is_default)
        show_default: Показывать ли предустановленные категории
    
    Returns:
        InlineKeyboardMarkup: Клавиатура с категориями
    """
    builder = InlineKeyboardBuilder()
    
    # Разделяем категории на предустановленные и пользовательские
    default_cats = [c for c in categories if c[3]]
    custom_cats = [c for c in categories if not c[3]]
    
    # Пользовательские категории
    if custom_cats:
        for cat_id, name, emoji, _ in custom_cats:
            builder.button(
                text=f"{emoji} {name}",
                callback_data=f"cat:edit:{cat_id}"
            )
    
    if not custom_cats:
        builder.row(
            InlineKeyboardButton(
                text="🚫 Нет пользовательских категорий",
                callback_data="cat:none"
            )
        )
    
    builder.adjust(2)
    
    # Показать предустановленные
    if show_default and default_cats:
        builder.row(
            InlineKeyboardButton(
                text="📌 Предустановленные категории",
                callback_data="cat:show_default"
            )
        )
    
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="cat:back")
    )
    
    return builder.as_markup()


## Меню редактирования категории
def get_category_edit_menu(is_default: bool = False) -> InlineKeyboardMarkup:
    """
    Создает меню для редактирования категории.
    
    Args:
        is_default: Является ли категория предустановленной
    
    Returns:
        InlineKeyboardMarkup: Клавиатура с действиями
    """
    builder = InlineKeyboardBuilder()
    
    if not is_default:
        builder.row(
            InlineKeyboardButton(text="✏️ Изменить название", callback_data="catedit:name")
        )
        builder.row(
            InlineKeyboardButton(text="🎨 Изменить эмодзи", callback_data="catedit:emoji")
        )
        builder.row(
            InlineKeyboardButton(text="🗑 Удалить категорию", callback_data="catedit:delete")
        )
    else:
        builder.row(
            InlineKeyboardButton(
                text="🔒 Предустановленная категория",
                callback_data="cat:locked"
            )
        )
    
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="cat:view_my")
    )
    
    return builder.as_markup()


## Клавиатура подтверждения удаления
def get_delete_confirmation_keyboard(category_id: int) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для подтверждения удаления категории.
    
    Args:
        category_id: ID категории для удаления
    
    Returns:
        InlineKeyboardMarkup: Клавиатура подтверждения
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✅ Да, удалить",
            callback_data=f"catdel:confirm:{category_id}"
        ),
        InlineKeyboardButton(
            text="❌ Отмена",
            callback_data=f"cat:edit:{category_id}"
        )
    )
    return builder.as_markup()


## Клавиатура отмены
def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопкой отмены.
    
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопкой отмены
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="❌ Отмена", callback_data="cat:cancel")
    )
    return builder.as_markup()

