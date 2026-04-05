"""
Клавиатуры для работы с голосовыми транзакциями.

Поддержка мультиязычности через locales.
"""

from typing import List
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.locales import t, translate_category_name


## Клавиатура подтверждения голосовой транзакции
def get_voice_confirmation_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для подтверждения голосовой транзакции.

    :param lang: Код языка
    :return: InlineKeyboardMarkup
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=f"\u2705 {t('confirm', lang)}", callback_data="voice:confirm"),
        InlineKeyboardButton(text=f"\u270f\ufe0f {t('edit', lang)}", callback_data="voice:edit")
    )
    builder.row(
        InlineKeyboardButton(text=f"\u274c {t('cancel', lang)}", callback_data="voice:cancel")
    )
    return builder.as_markup()


## Клавиатура выбора поля для редактирования
def get_voice_edit_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для выбора поля для редактирования.

    :param lang: Код языка
    :return: InlineKeyboardMarkup
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=f"\U0001f4b5 {t('btn_amount', lang)}", callback_data="voice_edit:amount"),
        InlineKeyboardButton(text=f"\U0001f3f7 {t('btn_category', lang)}", callback_data="voice_edit:category")
    )
    builder.row(
        InlineKeyboardButton(text=f"\U0001f4dd {t('btn_description', lang)}", callback_data="voice_edit:description")
    )
    builder.row(
        InlineKeyboardButton(text=f"\u2b05\ufe0f {t('back', lang)}", callback_data="voice:back_to_confirm")
    )
    return builder.as_markup()


## Клавиатура с категориями для голосовой транзакции
def get_voice_categories_keyboard(categories: List[tuple], transaction_type: str, lang: str = "ru") -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для выбора категории при редактировании голосовой транзакции.

    :param categories: Список кортежей (id, name, emoji)
    :param transaction_type: Тип транзакции
    :param lang: Код языка
    :return: InlineKeyboardMarkup
    """
    builder = InlineKeyboardBuilder()

    for category_id, name, emoji in categories:
        display_name = translate_category_name(name, lang)
        button_text = f"{emoji} {display_name}"
        builder.button(
            text=button_text,
            callback_data=f"voice_cat:{category_id}"
        )

    builder.adjust(2)

    builder.row(
        InlineKeyboardButton(text=f"\u2b05\ufe0f {t('back', lang)}", callback_data="voice:back_to_edit_menu")
    )

    return builder.as_markup()


## Клавиатура отмены при редактировании
def get_voice_edit_cancel_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопкой возврата.

    :param lang: Код языка
    :return: InlineKeyboardMarkup
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=f"\u2b05\ufe0f {t('back', lang)}", callback_data="voice:back_to_edit_menu")
    )
    return builder.as_markup()
