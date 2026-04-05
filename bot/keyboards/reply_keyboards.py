"""
Клавиатуры Reply для постоянного меню.

Содержит функции для создания reply-клавиатур для постоянного доступа
к основным функциям бота. Поддержка мультиязычности через locales.
"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot.locales import t


def get_main_reply_keyboard(lang: str = "ru") -> ReplyKeyboardMarkup:
    """
    Создать постоянную Reply-клавиатуру с основными функциями.

    :param lang: Код языка
    :return: Reply-клавиатура с основными кнопками
    """
    builder = ReplyKeyboardBuilder()

    builder.row(
        KeyboardButton(text=f"\U0001f4b0 {t('btn_income', lang)}"),
        KeyboardButton(text=f"\U0001f4b8 {t('btn_expense', lang)}")
    )

    builder.row(
        KeyboardButton(text=f"\U0001f4ca {t('btn_stats', lang)}"),
        KeyboardButton(text=f"\u2795 {t('btn_add', lang)}")
    )

    builder.row(
        KeyboardButton(text=f"\U0001f4c2 {t('btn_more', lang)}")
    )

    return builder.as_markup(resize_keyboard=True)


def get_additional_menu_keyboard(lang: str = "ru") -> ReplyKeyboardMarkup:
    """
    Создать Reply-клавиатуру с дополнительными функциями.

    :param lang: Код языка
    :return: Reply-клавиатура с дополнительными кнопками
    """
    builder = ReplyKeyboardBuilder()

    builder.row(
        KeyboardButton(text=f"\U0001f4dd {t('btn_all_transactions', lang)}"),
        KeyboardButton(text=f"\U0001f4c5 {t('btn_by_period', lang)}")
    )

    builder.row(
        KeyboardButton(text=f"\U0001f3f7\ufe0f {t('btn_categories', lang)}"),
        KeyboardButton(text=f"\U0001f4e4 {t('btn_export', lang)}")
    )

    builder.row(
        KeyboardButton(text=f"\u2699\ufe0f {t('btn_settings', lang)}")
    )

    builder.row(
        KeyboardButton(text=f"\u25c0\ufe0f {t('btn_back', lang)}")
    )

    return builder.as_markup(resize_keyboard=True)
