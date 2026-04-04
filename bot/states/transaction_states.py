"""
Состояния FSM для добавления и редактирования транзакций.

Defines:
    AddTransactionStates: FSM states for adding a transaction
"""

from aiogram.fsm.state import State, StatesGroup


## Состояния для добавления транзакции
class AddTransactionStates(StatesGroup):
    """
    FSM состояния для процесса добавления транзакции.
    
    States:
        choosing_type: Выбор типа операции (доход/расход)
        entering_amount: Ввод суммы транзакции
        choosing_category: Выбор категории из списка
        entering_custom_category: Ввод пользовательской категории
        entering_description: Ввод описания (опционально)
        confirmation: Подтверждение транзакции перед сохранением
    """
    choosing_type = State()
    entering_amount = State()
    choosing_category = State()
    entering_custom_category = State()
    entering_description = State()
    confirmation = State()

