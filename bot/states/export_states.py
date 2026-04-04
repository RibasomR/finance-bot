"""
Состояния FSM для экспорта данных.

Содержит состояния для процесса экспорта транзакций в Excel.
"""

from aiogram.fsm.state import State, StatesGroup


## FSM для экспорта данных
class ExportStates(StatesGroup):
    """
    Состояния для процесса экспорта данных.
    
    :cvar selecting_period: Выбор периода для экспорта
    :cvar generating_file: Генерация файла (промежуточное состояние)
    """
    
    selecting_period = State()
    generating_file = State()

