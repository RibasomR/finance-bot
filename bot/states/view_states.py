"""
Состояния FSM для просмотра транзакций.

Содержит состояния для просмотра, редактирования и удаления транзакций.
"""

from aiogram.fsm.state import State, StatesGroup


## FSM для просмотра транзакций
class ViewTransactionsStates(StatesGroup):
    """
    Состояния для просмотра и управления транзакциями.
    
    :cvar viewing_list: Просмотр списка транзакций
    :cvar confirm_delete: Подтверждение удаления транзакции
    """
    
    viewing_list = State()
    confirm_delete = State()


## FSM для редактирования транзакции
class EditTransactionStates(StatesGroup):
    """
    Состояния для редактирования транзакции.
    
    :cvar selecting_field: Выбор поля для редактирования
    :cvar editing_amount: Редактирование суммы
    :cvar editing_category: Редактирование категории
    :cvar editing_description: Редактирование описания
    """
    
    selecting_field = State()
    editing_amount = State()
    editing_category = State()
    editing_description = State()

