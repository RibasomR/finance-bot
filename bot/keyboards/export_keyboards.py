"""
Клавиатуры для функционала экспорта данных.

Поддержка мультиязычности через locales.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.locales import t


## Клавиатура выбора периода для экспорта
def get_export_period_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """
    Создать клавиатуру для выбора периода экспорта.

    :param lang: Код языка
    :return: Inline клавиатура
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=f"\U0001f4c5 {t('export_btn_today', lang)}", callback_data="export:today"),
            ],
            [
                InlineKeyboardButton(text=f"\U0001f5d3 {t('export_btn_yesterday', lang)}", callback_data="export:yesterday"),
            ],
            [
                InlineKeyboardButton(text=f"\U0001f4c6 {t('export_btn_week', lang)}", callback_data="export:week"),
            ],
            [
                InlineKeyboardButton(text=f"\U0001f4c5 {t('export_btn_month', lang)}", callback_data="export:month"),
            ],
            [
                InlineKeyboardButton(text=f"\U0001f5d3 {t('export_btn_year', lang)}", callback_data="export:year"),
            ],
            [
                InlineKeyboardButton(text=f"\U0001f4ca {t('export_btn_all', lang)}", callback_data="export:all"),
            ],
            [
                InlineKeyboardButton(text=f"\u274c {t('cancel', lang)}", callback_data="menu:main"),
            ],
        ]
    )
    return keyboard
