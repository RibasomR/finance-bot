"""
Клавиатуры для работы с транзакциями.

Functions:
    get_transaction_type_keyboard: Клавиатура выбора типа операции
    get_categories_keyboard: Клавиатура выбора категории
    get_confirmation_keyboard: Клавиатура подтверждения транзакции
    get_cancel_keyboard: Клавиатура с кнопкой отмены
"""

from typing import List
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


## Клавиатура выбора типа операции
def get_transaction_type_keyboard() -> InlineKeyboardMarkup:
    """
    Создает inline-клавиатуру для выбора типа транзакции.
    
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками "Доход" и "Расход"
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="💰 Доход", callback_data="type:income"),
        InlineKeyboardButton(text="💸 Расход", callback_data="type:expense")
    )
    builder.row(
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")
    )
    return builder.as_markup()


## Клавиатура выбора категории
def get_categories_keyboard(categories: List[tuple], transaction_type: str) -> InlineKeyboardMarkup:
    """
    Создает inline-клавиатуру для выбора категории транзакции.
    
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
            callback_data=f"category:{category_id}"
        )
    
    # 2 кнопки в ряд для компактности
    builder.adjust(2)
    
    # Кнопка "Другое" и "Отмена"
    builder.row(
        InlineKeyboardButton(text="✏️ Другое", callback_data="category:custom")
    )
    builder.row(
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")
    )
    
    return builder.as_markup()


## Клавиатура подтверждения
def get_confirmation_keyboard() -> InlineKeyboardMarkup:
    """
    Создает inline-клавиатуру для подтверждения транзакции.
    
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками подтверждения
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm:yes"),
        InlineKeyboardButton(text="❌ Отменить", callback_data="confirm:no")
    )
    return builder.as_markup()


## Клавиатура с кнопкой пропуска и отмены
def get_cancel_keyboard(skip_button: bool = False) -> InlineKeyboardMarkup:
    """
    Создает inline-клавиатуру с кнопкой отмены и опционально кнопкой пропуска.
    
    Args:
        skip_button: Добавить ли кнопку "Пропустить"
    
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками
    """
    builder = InlineKeyboardBuilder()
    
    if skip_button:
        builder.row(
            InlineKeyboardButton(text="⏭ Пропустить", callback_data="skip")
        )
    
    builder.row(
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")
    )
    
    return builder.as_markup()

