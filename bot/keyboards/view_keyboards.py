"""
Клавиатуры для просмотра транзакций и главного меню.

Содержит функции для создания inline-клавиатур для просмотра транзакций,
статистики, фильтров и главного меню.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Optional


## Главное меню бота
def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Создать главное меню бота.
    
    :return: Inline-клавиатура с главным меню
    
    Example:
        >>> keyboard = get_main_menu_keyboard()
        >>> await message.answer("Главное меню:", reply_markup=keyboard)
    """
    keyboard = [
        [InlineKeyboardButton(text="📊 Статистика", callback_data="menu:stats")],
        [InlineKeyboardButton(text="📝 Все транзакции", callback_data="menu:all")],
        [
            InlineKeyboardButton(text="💰 Доходы", callback_data="menu:income"),
            InlineKeyboardButton(text="💸 Расходы", callback_data="menu:expense"),
        ],
        [InlineKeyboardButton(text="📅 За период", callback_data="menu:period")],
        [InlineKeyboardButton(text="🏷️ Категории", callback_data="menu:categories")],
        [
            InlineKeyboardButton(text="📤 Экспорт", callback_data="menu:export"),
            InlineKeyboardButton(text="⚙️ Настройки", callback_data="menu:settings"),
        ],
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


## Клавиатура навигации по транзакциям
def get_transactions_navigation_keyboard(
    page: int,
    total_pages: int,
    transactions_info: list[dict],
    transaction_type: Optional[str] = None,
    period_filter: Optional[str] = None
) -> InlineKeyboardMarkup:
    """
    Создать клавиатуру навигации по списку транзакций с кнопками для каждой транзакции.
    
    :param page: Текущая страница (начиная с 1)
    :param total_pages: Всего страниц
    :param transactions_info: Список словарей с информацией о транзакциях:
        [{"id": int, "description": str, "amount": float, "category_name": str}]
    :param transaction_type: Фильтр по типу транзакции (all/income/expense)
    :param period_filter: Фильтр по периоду
    :return: Inline-клавиатура с кнопками навигации и транзакций
    
    Example:
        >>> keyboard = get_transactions_navigation_keyboard(
        ...     page=1, total_pages=5, 
        ...     transactions_info=[{"id": 1, "description": "молоко", "amount": 100.0, "category_name": "Продукты"}]
        ... )
        >>> await message.answer("Транзакции:", reply_markup=keyboard)
    """
    buttons = []
    
    # Кнопки для транзакций (по 1 в ряд для читаемости)
    for tr_info in transactions_info:
        tr_id = tr_info["id"]
        description = tr_info.get("description", "")
        amount = tr_info["amount"]
        category_name = tr_info["category_name"]
        currency_symbol = tr_info.get("currency_symbol", "₽")
        
        # Формируем текст кнопки: "описание | сумма | категория"
        # Если описания нет, используем только сумму и категорию
        if description and description != "Без описания":
            # Ограничиваем длину описания
            desc_short = description[:25] + "..." if len(description) > 25 else description
            button_text = f"{desc_short} | {amount:.0f} {currency_symbol} | {category_name}"
        else:
            button_text = f"{amount:.0f} {currency_symbol} | {category_name}"
        
        # Ограничиваем общую длину кнопки до 64 символов (лимит Telegram)
        if len(button_text) > 64:
            if description and description != "Без описания":
                # Сокращаем описание
                base_len = len(f" | {amount:.0f} {currency_symbol} | {category_name}")
                max_desc_len = max(10, 64 - base_len - 3)  # Минимум 10 символов для описания
                desc_short = description[:max_desc_len] + "..." if len(description) > max_desc_len else description
                button_text = f"{desc_short} | {amount:.0f} {currency_symbol} | {category_name}"
                
                # Если всё равно не влезает, убираем категорию
                if len(button_text) > 64:
                    base_len = len(f" | {amount:.0f} {currency_symbol}")
                    max_desc_len = max(10, 64 - base_len - 3)
                    desc_short = description[:max_desc_len] + "..." if len(description) > max_desc_len else description
                    button_text = f"{desc_short} | {amount:.0f} {currency_symbol}"
            else:
                # Если нет описания, сокращаем категорию
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
        nav_row.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=callback))
    
    nav_row.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="nav:page"))
    
    if page < total_pages:
        callback = f"nav:next:{page+1}"
        if transaction_type:
            callback += f":{transaction_type}"
        if period_filter:
            callback += f":{period_filter}"
        nav_row.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=callback))
    
    buttons.append(nav_row)
    
    # Кнопка возврата в меню
    buttons.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu:main")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


## Клавиатура для одной транзакции
def get_transaction_actions_keyboard(transaction_id: int) -> InlineKeyboardMarkup:
    """
    Создать клавиатуру с действиями для конкретной транзакции.
    
    :param transaction_id: ID транзакции
    :return: Inline-клавиатура с кнопками действий
    
    Example:
        >>> keyboard = get_transaction_actions_keyboard(transaction_id=123)
        >>> await message.answer("Что сделать?", reply_markup=keyboard)
    """
    keyboard = [
        [
            InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit:{transaction_id}"),
            InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete:{transaction_id}"),
        ],
        [InlineKeyboardButton(text="◀️ Назад к списку", callback_data="back:list")],
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


## Клавиатура подтверждения удаления
def get_delete_confirmation_keyboard(transaction_id: int) -> InlineKeyboardMarkup:
    """
    Создать клавиатуру подтверждения удаления транзакции.
    
    :param transaction_id: ID транзакции
    :return: Inline-клавиатура с кнопками подтверждения
    
    Example:
        >>> keyboard = get_delete_confirmation_keyboard(transaction_id=123)
        >>> await message.answer("Удалить?", reply_markup=keyboard)
    """
    keyboard = [
        [
            InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"delete:confirm:{transaction_id}"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="delete:cancel"),
        ],
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


## Клавиатура с кнопкой редактирования для сохранённой транзакции
def get_edit_transaction_button(transaction_id: int) -> InlineKeyboardMarkup:
    """
    Создать клавиатуру с кнопкой редактирования для только что сохранённой транзакции.
    
    :param transaction_id: ID транзакции
    :return: Inline-клавиатура с кнопкой редактирования
    
    Example:
        >>> keyboard = get_edit_transaction_button(transaction_id=123)
        >>> await message.answer("Транзакция сохранена!", reply_markup=keyboard)
    """
    keyboard = [
        [InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit:{transaction_id}")],
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


## Клавиатура выбора периода
def get_period_filter_keyboard() -> InlineKeyboardMarkup:
    """
    Создать клавиатуру выбора периода для фильтрации транзакций.
    
    :return: Inline-клавиатура с вариантами периодов
    
    Example:
        >>> keyboard = get_period_filter_keyboard()
        >>> await message.answer("Выберите период:", reply_markup=keyboard)
    """
    keyboard = [
        [
            InlineKeyboardButton(text="Сегодня", callback_data="period:today"),
            InlineKeyboardButton(text="Вчера", callback_data="period:yesterday"),
        ],
        [
            InlineKeyboardButton(text="Неделя", callback_data="period:week"),
            InlineKeyboardButton(text="Месяц", callback_data="period:month"),
        ],
        [
            InlineKeyboardButton(text="Год", callback_data="period:year"),
            InlineKeyboardButton(text="Всё время", callback_data="period:all"),
        ],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="menu:main")],
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


## Клавиатура выбора поля для редактирования
def get_edit_field_keyboard(transaction_id: int) -> InlineKeyboardMarkup:
    """
    Создать клавиатуру выбора поля для редактирования транзакции.
    
    :param transaction_id: ID транзакции
    :return: Inline-клавиатура с полями для редактирования
    
    Example:
        >>> keyboard = get_edit_field_keyboard(transaction_id=123)
        >>> await message.answer("Что изменить?", reply_markup=keyboard)
    """
    keyboard = [
        [InlineKeyboardButton(text="💵 Сумма", callback_data=f"edit:field:amount:{transaction_id}")],
        [InlineKeyboardButton(text="🏷 Категория", callback_data=f"edit:field:category:{transaction_id}")],
        [InlineKeyboardButton(text="📝 Описание", callback_data=f"edit:field:description:{transaction_id}")],
        [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete:{transaction_id}")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="edit:cancel")],
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


## Клавиатура для одной транзакции в списке
def get_transaction_inline_button(transaction_id: int, index: int) -> InlineKeyboardMarkup:
    """
    Создать inline-кнопку для транзакции в списке.
    
    :param transaction_id: ID транзакции
    :param index: Порядковый номер транзакции в списке
    :return: Inline-клавиатура с кнопкой редактирования
    
    Example:
        >>> keyboard = get_transaction_inline_button(transaction_id=123, index=1)
        >>> await message.answer("Транзакция:", reply_markup=keyboard)
    """
    keyboard = [
        [InlineKeyboardButton(text=f"✏️ Изменить #{index}", callback_data=f"edit:{transaction_id}")],
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

