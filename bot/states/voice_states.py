"""
Состояния FSM для голосового ввода транзакций.

Defines:
    VoiceTransactionStates: FSM states for voice transaction confirmation and editing
"""

from aiogram.fsm.state import State, StatesGroup


## Состояния для обработки голосовой транзакции
class VoiceTransactionStates(StatesGroup):
    """
    FSM состояния для подтверждения и редактирования голосовой транзакции.
    
    States:
        waiting_confirmation: Ожидание подтверждения распознанной транзакции
        editing_amount: Редактирование суммы
        editing_category: Редактирование категории
        editing_description: Редактирование описания
    """
    waiting_confirmation = State()
    editing_amount = State()
    editing_category = State()
    editing_description = State()

