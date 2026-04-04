"""
Клавиатуры для работы с голосовыми транзакциями.

Functions:
    get_voice_confirmation_keyboard: Клавиатура подтверждения голосовой транзакции
    get_voice_edit_keyboard: Клавиатура выбора поля для редактирования
"""

from typing import List
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


## Клавиатура подтверждения голосовой транзакции
def get_voice_confirmation_keyboard() -> InlineKeyboardMarkup:
    """
    Создает inline-клавиатуру для подтверждения голосовой транзакции.
    
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками подтверждения, отмены и редактирования
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Подтвердить", callback_data="voice:confirm"),
        InlineKeyboardButton(text="✏️ Редактировать", callback_data="voice:edit")
    )
    builder.row(
        InlineKeyboardButton(text="❌ Отменить", callback_data="voice:cancel")
    )
    return builder.as_markup()


## Клавиатура выбора поля для редактирования
def get_voice_edit_keyboard() -> InlineKeyboardMarkup:
    """
    Создает inline-клавиатуру для выбора поля голосовой транзакции для редактирования.
    
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками выбора полей
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="💵 Сумма", callback_data="voice_edit:amount"),
        InlineKeyboardButton(text="🏷 Категория", callback_data="voice_edit:category")
    )
    builder.row(
        InlineKeyboardButton(text="📝 Описание", callback_data="voice_edit:description")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="voice:back_to_confirm")
    )
    return builder.as_markup()


## Клавиатура с категориями для голосовой транзакции
def get_voice_categories_keyboard(categories: List[tuple], transaction_type: str) -> InlineKeyboardMarkup:
    """
    Создает inline-клавиатуру для выбора категории при редактировании голосовой транзакции.
    
    Args:
        categories: Список кортежей (id, name, emoji) категорий
        transaction_type: Тип транзакции ('income' или 'expense')
    
    Returns:
        InlineKeyboardMarkup: Клавиатура с категориями
    """
    builder = InlineKeyboardBuilder()
    
    for category_id, name, emoji in categories:
        button_text = f"{emoji} {name}"
        builder.button(
            text=button_text,
            callback_data=f"voice_cat:{category_id}"
        )
    
    # 2 кнопки в ряд для компактности
    builder.adjust(2)
    
    # Кнопка "Назад"
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="voice:back_to_edit_menu")
    )
    
    return builder.as_markup()


## Клавиатура отмены при редактировании
def get_voice_edit_cancel_keyboard() -> InlineKeyboardMarkup:
    """
    Создает inline-клавиатуру с кнопкой отмены редактирования.
    
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопкой отмены
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="voice:back_to_edit_menu")
    )
    return builder.as_markup()

