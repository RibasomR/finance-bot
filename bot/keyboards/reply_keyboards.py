"""
Клавиатуры Reply для постоянного меню.

Содержит функции для создания reply-клавиатур для постоянного доступа
к основным функциям бота.
"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_main_reply_keyboard() -> ReplyKeyboardMarkup:
    """
    Создать постоянную Reply-клавиатуру с основными функциями.
    
    Клавиатура содержит кнопки для быстрого доступа к основным функциям:
    - Доходы и Расходы (просмотр списков)
    - Статистика
    - Добавить транзакцию
    - Дополнительное меню (категории, экспорт, настройки)
    
    :return: Reply-клавиатура с основными кнопками
    
    Example:
        >>> keyboard = get_main_reply_keyboard()
        >>> await message.answer("Главное меню:", reply_markup=keyboard)
    """
    builder = ReplyKeyboardBuilder()
    
    # Первый ряд - доходы и расходы
    builder.row(
        KeyboardButton(text="💰 Доходы"),
        KeyboardButton(text="💸 Расходы")
    )
    
    # Второй ряд - статистика и добавить
    builder.row(
        KeyboardButton(text="📊 Статистика"),
        KeyboardButton(text="➕ Добавить")
    )
    
    # Третий ряд - дополнительное меню
    builder.row(
        KeyboardButton(text="📂 Ещё")
    )
    
    return builder.as_markup(resize_keyboard=True)


def get_additional_menu_keyboard() -> ReplyKeyboardMarkup:
    """
    Создать Reply-клавиатуру с дополнительными функциями.
    
    Содержит второстепенные функции:
    - Все транзакции
    - За период
    - Категории
    - Экспорт
    - Настройки
    
    :return: Reply-клавиатура с дополнительными кнопками
    
    Example:
        >>> keyboard = get_additional_menu_keyboard()
        >>> await message.answer("Дополнительно:", reply_markup=keyboard)
    """
    builder = ReplyKeyboardBuilder()
    
    # Первый ряд - все транзакции и период
    builder.row(
        KeyboardButton(text="📝 Все транзакции"),
        KeyboardButton(text="📅 За период")
    )
    
    # Второй ряд - категории и экспорт
    builder.row(
        KeyboardButton(text="🏷️ Категории"),
        KeyboardButton(text="📤 Экспорт")
    )
    
    # Третий ряд - настройки
    builder.row(
        KeyboardButton(text="⚙️ Настройки")
    )
    
    # Четвертый ряд - назад
    builder.row(
        KeyboardButton(text="◀️ Назад")
    )
    
    return builder.as_markup(resize_keyboard=True)

