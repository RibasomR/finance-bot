"""
Клавиатуры для управления категориями.

Поддержка мультиязычности через locales.
"""

from typing import List
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.locales import t, translate_category_name


## Главное меню управления категориями
def get_category_management_menu(lang: str = "ru") -> InlineKeyboardMarkup:
    """
    Создает главное меню управления категориями.

    :param lang: Код языка
    :return: InlineKeyboardMarkup
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=f"\U0001f4cb {t('cat_my_categories', lang)}", callback_data="cat:view_my")
    )
    builder.row(
        InlineKeyboardButton(text=f"\u2795 {t('cat_add', lang)}", callback_data="cat:add")
    )
    builder.row(
        InlineKeyboardButton(text=f"\U0001f519 {t('menu_back', lang)}", callback_data="back_to_menu")
    )
    return builder.as_markup()


## Клавиатура выбора типа категории
def get_category_type_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для выбора типа категории.

    :param lang: Код языка
    :return: InlineKeyboardMarkup
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=f"\U0001f4b0 {t('tx_type_income', lang)}", callback_data="cattype:income"),
        InlineKeyboardButton(text=f"\U0001f4b8 {t('tx_type_expense', lang)}", callback_data="cattype:expense")
    )
    builder.row(
        InlineKeyboardButton(text=f"\u274c {t('cancel', lang)}", callback_data="cat:cancel")
    )
    return builder.as_markup()


## Клавиатура с пользовательскими категориями
def get_user_categories_keyboard(
    categories: List[tuple],
    show_default: bool = False,
    lang: str = "ru"
) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру со списком категорий пользователя.

    :param categories: Список кортежей (id, name, emoji, is_default)
    :param show_default: Показывать ли предустановленные
    :param lang: Код языка
    :return: InlineKeyboardMarkup
    """
    builder = InlineKeyboardBuilder()

    default_cats = [c for c in categories if c[3]]
    custom_cats = [c for c in categories if not c[3]]

    if custom_cats:
        for cat_id, name, emoji, _ in custom_cats:
            builder.button(
                text=f"{emoji} {name}",
                callback_data=f"cat:edit:{cat_id}"
            )

    if not custom_cats:
        builder.row(
            InlineKeyboardButton(
                text=f"\U0001f6ab {t('cat_btn_no_custom', lang)}",
                callback_data="cat:none"
            )
        )

    builder.adjust(2)

    if show_default and default_cats:
        builder.row(
            InlineKeyboardButton(
                text=f"\U0001f4cc {t('cat_btn_show_default', lang)}",
                callback_data="cat:show_default"
            )
        )

    builder.row(
        InlineKeyboardButton(text=f"\U0001f519 {t('back', lang)}", callback_data="cat:back")
    )

    return builder.as_markup()


## Меню редактирования категории
def get_category_edit_menu(is_default: bool = False, lang: str = "ru") -> InlineKeyboardMarkup:
    """
    Создает меню для редактирования категории.

    :param is_default: Является ли категория предустановленной
    :param lang: Код языка
    :return: InlineKeyboardMarkup
    """
    builder = InlineKeyboardBuilder()

    if not is_default:
        builder.row(
            InlineKeyboardButton(text=f"\u270f\ufe0f {t('cat_btn_edit_name', lang)}", callback_data="catedit:name")
        )
        builder.row(
            InlineKeyboardButton(text=f"\U0001f3a8 {t('cat_btn_edit_emoji', lang)}", callback_data="catedit:emoji")
        )
        builder.row(
            InlineKeyboardButton(text=f"\U0001f5d1 {t('cat_btn_delete', lang)}", callback_data="catedit:delete")
        )
    else:
        builder.row(
            InlineKeyboardButton(
                text=f"\U0001f512 {t('cat_btn_locked', lang)}",
                callback_data="cat:locked"
            )
        )

    builder.row(
        InlineKeyboardButton(text=f"\U0001f519 {t('back', lang)}", callback_data="cat:view_my")
    )

    return builder.as_markup()


## Клавиатура подтверждения удаления
def get_delete_confirmation_keyboard(category_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для подтверждения удаления.

    :param category_id: ID категории
    :param lang: Код языка
    :return: InlineKeyboardMarkup
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=f"\u2705 {t('yes_delete', lang)}",
            callback_data=f"catdel:confirm:{category_id}"
        ),
        InlineKeyboardButton(
            text=f"\u274c {t('cancel', lang)}",
            callback_data=f"cat:edit:{category_id}"
        )
    )
    return builder.as_markup()


## Клавиатура отмены
def get_cancel_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопкой отмены.

    :param lang: Код языка
    :return: InlineKeyboardMarkup
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=f"\u274c {t('cancel', lang)}", callback_data="cat:cancel")
    )
    return builder.as_markup()
