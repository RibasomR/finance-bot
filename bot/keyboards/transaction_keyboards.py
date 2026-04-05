"""
Клавиатуры для работы с транзакциями.

Поддержка мультиязычности через locales.
"""

from typing import List
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.locales import t


## Клавиатура выбора типа операции
def get_transaction_type_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """
    Создает inline-клавиатуру для выбора типа транзакции.

    :param lang: Код языка
    :return: InlineKeyboardMarkup
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=f"\U0001f4b0 {t('tx_type_income', lang)}", callback_data="type:income"),
        InlineKeyboardButton(text=f"\U0001f4b8 {t('tx_type_expense', lang)}", callback_data="type:expense")
    )
    builder.row(
        InlineKeyboardButton(text=f"\u274c {t('cancel', lang)}", callback_data="cancel")
    )
    return builder.as_markup()


## Клавиатура выбора категории
def get_categories_keyboard(categories: List[tuple], transaction_type: str, lang: str = "ru") -> InlineKeyboardMarkup:
    """
    Создает inline-клавиатуру для выбора категории.

    :param categories: Список кортежей (id, name, emoji)
    :param transaction_type: Тип транзакции
    :param lang: Код языка
    :return: InlineKeyboardMarkup
    """
    from bot.locales import translate_category_name

    builder = InlineKeyboardBuilder()

    for category_id, name, emoji in categories:
        display_name = translate_category_name(name, lang)
        button_text = f"{emoji} {display_name}"
        builder.button(
            text=button_text,
            callback_data=f"category:{category_id}"
        )

    builder.adjust(2)

    builder.row(
        InlineKeyboardButton(text=f"\u270f\ufe0f {t('tx_custom_category', lang)}", callback_data="category:custom")
    )
    builder.row(
        InlineKeyboardButton(text=f"\u274c {t('cancel', lang)}", callback_data="cancel")
    )

    return builder.as_markup()


## Клавиатура подтверждения
def get_confirmation_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """
    Создает inline-клавиатуру для подтверждения транзакции.

    :param lang: Код языка
    :return: InlineKeyboardMarkup
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=f"\u2705 {t('confirm', lang)}", callback_data="confirm:yes"),
        InlineKeyboardButton(text=f"\u274c {t('cancel', lang)}", callback_data="confirm:no")
    )
    return builder.as_markup()


## Клавиатура с кнопкой пропуска и отмены
def get_cancel_keyboard(skip_button: bool = False, lang: str = "ru") -> InlineKeyboardMarkup:
    """
    Создает inline-клавиатуру с кнопкой отмены.

    :param skip_button: Добавить ли кнопку "Пропустить"
    :param lang: Код языка
    :return: InlineKeyboardMarkup
    """
    builder = InlineKeyboardBuilder()

    if skip_button:
        builder.row(
            InlineKeyboardButton(text=f"\u23ed {t('skip', lang)}", callback_data="skip")
        )

    builder.row(
        InlineKeyboardButton(text=f"\u274c {t('cancel', lang)}", callback_data="cancel")
    )

    return builder.as_markup()
