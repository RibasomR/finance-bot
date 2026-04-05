"""
Клавиатуры для просмотра транзакций и главного меню.

Содержит функции для создания inline-клавиатур для просмотра транзакций,
статистики, фильтров и главного меню. Поддержка мультиязычности.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Optional

from bot.locales import t


## Главное меню бота
def get_main_menu_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """
    Создать главное меню бота.

    :param lang: Код языка
    :return: Inline-клавиатура с главным меню
    """
    keyboard = [
        [InlineKeyboardButton(text=f"\U0001f4ca {t('menu_stats', lang)}", callback_data="menu:stats")],
        [InlineKeyboardButton(text=f"\U0001f4dd {t('menu_all_transactions', lang)}", callback_data="menu:all")],
        [
            InlineKeyboardButton(text=f"\U0001f4b0 {t('menu_income', lang)}", callback_data="menu:income"),
            InlineKeyboardButton(text=f"\U0001f4b8 {t('menu_expense', lang)}", callback_data="menu:expense"),
        ],
        [InlineKeyboardButton(text=f"\U0001f4c5 {t('menu_period', lang)}", callback_data="menu:period")],
        [InlineKeyboardButton(text=f"\U0001f3f7\ufe0f {t('menu_categories', lang)}", callback_data="menu:categories")],
        [
            InlineKeyboardButton(text=f"\U0001f4e4 {t('menu_export', lang)}", callback_data="menu:export"),
            InlineKeyboardButton(text=f"\u2699\ufe0f {t('menu_settings', lang)}", callback_data="menu:settings"),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


## Клавиатура под статистикой
def get_stats_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text=f"\U0001f4c5 {t('menu_period', lang)}", callback_data="menu:period")],
        [InlineKeyboardButton(text=f"\U0001f4e4 {t('menu_export', lang)}", callback_data="stats:export")],
        [InlineKeyboardButton(text=f"\U0001f3f7\ufe0f {t('menu_categories', lang)}", callback_data="menu:categories")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


## Клавиатура навигации по транзакциям
def get_transactions_navigation_keyboard(
    page: int,
    total_pages: int,
    transactions_info: list[dict],
    transaction_type: Optional[str] = None,
    period_filter: Optional[str] = None,
    lang: str = "ru"
) -> InlineKeyboardMarkup:
    """
    Создать клавиатуру навигации по списку транзакций.

    :param page: Текущая страница
    :param total_pages: Всего страниц
    :param transactions_info: Информация о транзакциях
    :param transaction_type: Фильтр по типу
    :param period_filter: Фильтр по периоду
    :param lang: Код языка
    :return: Inline-клавиатура
    """
    buttons = []

    for tr_info in transactions_info:
        tr_id = tr_info["id"]
        description = tr_info.get("description", "")
        amount = tr_info["amount"]
        category_name = tr_info["category_name"]
        currency_symbol = tr_info.get("currency_symbol", "\u20bd")

        if description and description != "Без описания":
            desc_short = description[:25] + "..." if len(description) > 25 else description
            button_text = f"{desc_short} | {amount:.0f} {currency_symbol} | {category_name}"
        else:
            button_text = f"{amount:.0f} {currency_symbol} | {category_name}"

        if len(button_text) > 64:
            if description and description != "Без описания":
                base_len = len(f" | {amount:.0f} {currency_symbol} | {category_name}")
                max_desc_len = max(10, 64 - base_len - 3)
                desc_short = description[:max_desc_len] + "..." if len(description) > max_desc_len else description
                button_text = f"{desc_short} | {amount:.0f} {currency_symbol} | {category_name}"

                if len(button_text) > 64:
                    base_len = len(f" | {amount:.0f} {currency_symbol}")
                    max_desc_len = max(10, 64 - base_len - 3)
                    desc_short = description[:max_desc_len] + "..." if len(description) > max_desc_len else description
                    button_text = f"{desc_short} | {amount:.0f} {currency_symbol}"
            else:
                base_len = len(f"{amount:.0f} {currency_symbol} | ")
                max_cat_len = 64 - base_len
                cat_short = category_name[:max_cat_len] + "..." if len(category_name) > max_cat_len else category_name
                button_text = f"{amount:.0f} {currency_symbol} | {cat_short}"

        buttons.append([
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"edit:{tr_id}"
            )
        ])

    # Кнопки навигации
    nav_row = []
    if page > 1:
        callback = f"nav:prev:{page-1}"
        if transaction_type:
            callback += f":{transaction_type}"
        if period_filter:
            callback += f":{period_filter}"
        nav_row.append(InlineKeyboardButton(text=f"\u2b05\ufe0f {t('view_nav_prev', lang)}", callback_data=callback))

    nav_row.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="nav:page"))

    if page < total_pages:
        callback = f"nav:next:{page+1}"
        if transaction_type:
            callback += f":{transaction_type}"
        if period_filter:
            callback += f":{period_filter}"
        nav_row.append(InlineKeyboardButton(text=f"{t('view_nav_next', lang)} \u27a1\ufe0f", callback_data=callback))

    buttons.append(nav_row)

    buttons.append([InlineKeyboardButton(text=f"\U0001f3e0 {t('menu_home', lang)}", callback_data="menu:main")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


## Клавиатура для одной транзакции
def get_transaction_actions_keyboard(transaction_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    """
    Создать клавиатуру с действиями для конкретной транзакции.

    :param transaction_id: ID транзакции
    :param lang: Код языка
    :return: Inline-клавиатура
    """
    keyboard = [
        [
            InlineKeyboardButton(text=f"\u270f\ufe0f {t('edit', lang)}", callback_data=f"edit:{transaction_id}"),
            InlineKeyboardButton(text=f"\U0001f5d1 {t('btn_delete', lang)}", callback_data=f"delete:{transaction_id}"),
        ],
        [InlineKeyboardButton(text=f"\u25c0\ufe0f {t('back', lang)}", callback_data="back:list")],
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


## Клавиатура подтверждения удаления
def get_delete_confirmation_keyboard(transaction_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    """
    Создать клавиатуру подтверждения удаления.

    :param transaction_id: ID транзакции
    :param lang: Код языка
    :return: Inline-клавиатура
    """
    keyboard = [
        [
            InlineKeyboardButton(text=f"\u2705 {t('yes_delete', lang)}", callback_data=f"delete:confirm:{transaction_id}"),
            InlineKeyboardButton(text=f"\u274c {t('cancel', lang)}", callback_data="delete:cancel"),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


## Кнопка редактирования для сохранённой транзакции
def get_edit_transaction_button(transaction_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    """
    Создать клавиатуру с кнопкой редактирования.

    :param transaction_id: ID транзакции
    :param lang: Код языка
    :return: Inline-клавиатура
    """
    keyboard = [
        [InlineKeyboardButton(text=f"\u270f\ufe0f {t('edit', lang)}", callback_data=f"edit:{transaction_id}")],
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


## Клавиатура выбора периода
def get_period_filter_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """
    Создать клавиатуру выбора периода для фильтрации.

    :param lang: Код языка
    :return: Inline-клавиатура
    """
    keyboard = [
        [
            InlineKeyboardButton(text=t("period_today", lang), callback_data="period:today"),
            InlineKeyboardButton(text=t("period_yesterday", lang), callback_data="period:yesterday"),
        ],
        [
            InlineKeyboardButton(text=t("period_week", lang), callback_data="period:week"),
            InlineKeyboardButton(text=t("period_month", lang), callback_data="period:month"),
        ],
        [
            InlineKeyboardButton(text=t("period_year", lang), callback_data="period:year"),
            InlineKeyboardButton(text=t("period_all", lang), callback_data="period:all"),
        ],
        [InlineKeyboardButton(text=f"\u25c0\ufe0f {t('back', lang)}", callback_data="menu:main")],
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


## Клавиатура выбора поля для редактирования
def get_edit_field_keyboard(transaction_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    """
    Создать клавиатуру выбора поля для редактирования.

    :param transaction_id: ID транзакции
    :param lang: Код языка
    :return: Inline-клавиатура
    """
    keyboard = [
        [InlineKeyboardButton(text=f"\U0001f4b5 {t('btn_amount', lang)}", callback_data=f"edit:field:amount:{transaction_id}")],
        [InlineKeyboardButton(text=f"\U0001f3f7 {t('btn_category', lang)}", callback_data=f"edit:field:category:{transaction_id}")],
        [InlineKeyboardButton(text=f"\U0001f4dd {t('btn_description', lang)}", callback_data=f"edit:field:description:{transaction_id}")],
        [InlineKeyboardButton(text=f"\U0001f5d1 {t('btn_delete', lang)}", callback_data=f"delete:{transaction_id}")],
        [InlineKeyboardButton(text=f"\u274c {t('cancel', lang)}", callback_data="edit:cancel")],
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


## Клавиатура для одной транзакции в списке
def get_transaction_inline_button(transaction_id: int, index: int, lang: str = "ru") -> InlineKeyboardMarkup:
    """
    Создать inline-кнопку для транзакции в списке.

    :param transaction_id: ID транзакции
    :param index: Порядковый номер
    :param lang: Код языка
    :return: Inline-клавиатура
    """
    keyboard = [
        [InlineKeyboardButton(text=f"\u270f\ufe0f {t('edit', lang)} #{index}", callback_data=f"edit:{transaction_id}")],
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
