"""
Состояния FSM для управления категориями.

States:
    CategoryStates: Состояния для добавления/редактирования категорий
"""

from aiogram.fsm.state import State, StatesGroup


## Состояния управления категориями
class CategoryStates(StatesGroup):
    """
    Группа состояний для управления категориями.
    
    :cvar choosing_action: Выбор действия (добавить/редактировать/удалить)
    :cvar choosing_type: Выбор типа категории (доход/расход)
    :cvar entering_name: Ввод названия категории
    :cvar entering_emoji: Ввод эмодзи для категории
    :cvar confirming: Подтверждение создания/редактирования
    :cvar editing_category: Редактирование существующей категории
    :cvar choosing_edit_field: Выбор поля для редактирования
    """
    
    choosing_action = State()
    choosing_type = State()
    entering_name = State()
    entering_emoji = State()
    confirming = State()
    editing_category = State()
    choosing_edit_field = State()

