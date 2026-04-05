"""
Клавиатуры для раздела настроек пользователя.

Предоставляет inline-клавиатуры для управления настройками профиля.
Поддержка мультиязычности через locales.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.locales import t


## Главная клавиатура настроек
def get_settings_menu_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """
    Создать клавиатуру главного меню настроек.

    :param lang: Код языка
    :return: Inline-клавиатура
    """
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=f"\U0001f4b0 {t('settings_transaction_limit', lang)}",
            callback_data="settings:transaction_limit"
        )
    )

    builder.row(
        InlineKeyboardButton(
            text=f"\U0001f4ca {t('settings_monthly_limit', lang)}",
            callback_data="settings:monthly_limit"
        )
    )

    builder.row(
        InlineKeyboardButton(
            text=f"\U0001f4cb {t('settings_view_limits', lang)}",
            callback_data="settings:view_limits"
        )
    )

    builder.row(
        InlineKeyboardButton(
            text=f"\U0001f310 {t('settings_language', lang)}",
            callback_data="settings:language"
        )
    )

    builder.row(
        InlineKeyboardButton(
            text=f"\U0001f519 {t('menu_back', lang)}",
            callback_data="menu:main"
        )
    )

    return builder.as_markup()


## Клавиатура отмены настройки
def get_cancel_settings_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """
    Создать клавиатуру с кнопкой отмены.

    :param lang: Код языка
    :return: Inline-клавиатура
    """
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=f"\u274c {t('cancel', lang)}",
            callback_data="settings:cancel"
        )
    )

    return builder.as_markup()


## Клавиатура для удаления лимита
def get_remove_limit_keyboard(limit_type: str, lang: str = "ru") -> InlineKeyboardMarkup:
    """
    Создать клавиатуру с опциями управления лимитом.

    :param limit_type: Тип лимита
    :param lang: Код языка
    :return: Inline-клавиатура
    """
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=f"\U0001f5d1 {t('settings_btn_remove_limit', lang)}",
            callback_data=f"settings:remove_{limit_type}_limit"
        )
    )

    builder.row(
        InlineKeyboardButton(
            text=f"\u270f\ufe0f {t('settings_btn_change', lang)}",
            callback_data=f"settings:{limit_type}_limit"
        )
    )

    builder.row(
        InlineKeyboardButton(
            text=f"\U0001f519 {t('back', lang)}",
            callback_data="settings:menu"
        )
    )

    return builder.as_markup()
