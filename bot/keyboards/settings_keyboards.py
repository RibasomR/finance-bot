"""
Клавиатуры для раздела настроек пользователя.

Предоставляет inline-клавиатуры для управления настройками профиля.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


## Главная клавиатура настроек
def get_settings_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Создать клавиатуру главного меню настроек.
    
    Отображает доступные опции настроек профиля пользователя.
    
    :return: Inline-клавиатура с кнопками настроек
    
    Example:
        >>> keyboard = get_settings_menu_keyboard()
        >>> await message.answer("Настройки", reply_markup=keyboard)
    """
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="💰 Лимит одной транзакции",
            callback_data="settings:transaction_limit"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="📊 Месячный лимит трат",
            callback_data="settings:monthly_limit"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="📋 Мои текущие лимиты",
            callback_data="settings:view_limits"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад в меню",
            callback_data="menu:main"
        )
    )
    
    return builder.as_markup()


## Клавиатура отмены настройки
def get_cancel_settings_keyboard() -> InlineKeyboardMarkup:
    """
    Создать клавиатуру с кнопкой отмены.
    
    Используется при вводе значений настроек для возможности отмены.
    
    :return: Inline-клавиатура с кнопкой отмены
    
    Example:
        >>> keyboard = get_cancel_settings_keyboard()
        >>> await message.answer("Введи лимит", reply_markup=keyboard)
    """
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="❌ Отменить",
            callback_data="settings:cancel"
        )
    )
    
    return builder.as_markup()


## Клавиатура для удаления лимита
def get_remove_limit_keyboard(limit_type: str) -> InlineKeyboardMarkup:
    """
    Создать клавиатуру с опциями управления лимитом.
    
    :param limit_type: Тип лимита ('transaction' или 'monthly')
    :return: Inline-клавиатура
    
    Example:
        >>> keyboard = get_remove_limit_keyboard('transaction')
    """
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="🗑 Удалить лимит",
            callback_data=f"settings:remove_{limit_type}_limit"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="✏️ Изменить",
            callback_data=f"settings:{limit_type}_limit"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад",
            callback_data="settings:menu"
        )
    )
    
    return builder.as_markup()

