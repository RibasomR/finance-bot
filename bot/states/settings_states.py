"""
FSM состояния для настроек пользователя.

Управляет состояниями при изменении настроек лимитов транзакций.
"""

from aiogram.fsm.state import State, StatesGroup


## Состояния для настроек пользователя
class SettingsStates(StatesGroup):
    """
    Группа состояний для управления настройками пользователя.
    
    Используется при изменении лимитов транзакций и других настроек профиля.
    """
    
    waiting_for_transaction_limit = State()
    waiting_for_monthly_limit = State()

