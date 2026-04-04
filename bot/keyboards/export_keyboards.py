"""
Клавиатуры для функционала экспорта данных.

Содержит inline-клавиатуры для выбора периода экспорта.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


## Клавиатура выбора периода для экспорта
def get_export_period_keyboard() -> InlineKeyboardMarkup:
    """
    Создать клавиатуру для выбора периода экспорта.
    
    Предлагает пользователю выбрать период, за который
    будут экспортированы транзакции.
    
    :return: Inline клавиатура с вариантами периодов
    
    Example:
        >>> keyboard = get_export_period_keyboard()
        >>> await message.answer("Выберите период", reply_markup=keyboard)
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📅 Сегодня", callback_data="export:today"),
            ],
            [
                InlineKeyboardButton(text="🗓 Вчера", callback_data="export:yesterday"),
            ],
            [
                InlineKeyboardButton(text="📆 Неделя", callback_data="export:week"),
            ],
            [
                InlineKeyboardButton(text="📅 Месяц", callback_data="export:month"),
            ],
            [
                InlineKeyboardButton(text="🗓 Год", callback_data="export:year"),
            ],
            [
                InlineKeyboardButton(text="📊 Всё время", callback_data="export:all"),
            ],
            [
                InlineKeyboardButton(text="❌ Отменить", callback_data="menu:main"),
            ],
        ]
    )
    return keyboard

