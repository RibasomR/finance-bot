"""
Обработчики общих команд бота.

Содержит handlers для команд /start и /help.
"""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from loguru import logger

from bot.keyboards.reply_keyboards import get_main_reply_keyboard, get_additional_menu_keyboard
from bot.services.database import get_or_create_user

router = Router(name="common")


## Обработчик команды /start
@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    """
    Обработчик команды /start.
    
    Отправляет приветственное сообщение новому пользователю с кратким описанием
    возможностей бота и призывом к действию. Показывает постоянное меню.
    
    :param message: Объект сообщения от пользователя
    :return: None
    """
    user = message.from_user
    logger.info(f"Пользователь {user.id} (@{user.username}) запустил бота")
    
    # Создаём пользователя в БД
    await get_or_create_user(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
    )
    
    welcome_text = (
        f"👋 Привет, {user.first_name}!\n\n"
        "Я помогу вести учет твоих доходов и расходов.\n\n"
        "✨ <b>Что я умею:</b>\n"
        "• 🎤 Записывать транзакции голосом\n"
        "• ✍️ Добавлять операции вручную\n"
        "• 📊 Показывать статистику и аналитику\n"
        "• 📝 Вести историю всех операций\n"
        "• 📤 Экспортировать данные в Excel\n\n"
        "Используй меню ниже для быстрого доступа ко всем функциям 👇"
    )
    
    await message.answer(
        welcome_text, 
        parse_mode="HTML",
        reply_markup=get_main_reply_keyboard()
    )


## Обработчик команды /help
@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """
    Обработчик команды /help.
    
    Отправляет список всех доступных команд и функций бота
    с кратким описанием каждой функции.
    
    :param message: Объект сообщения от пользователя
    :return: None
    """
    logger.info(f"Пользователь {message.from_user.id} запросил помощь")
    
    help_text = (
        "📚 <b>Справка по боту</b>\n\n"
        
        "📝 <b>Добавление транзакций:</b>\n"
        "• 🎤 Отправь голосовое сообщение\n"
        "  Пример: <i>\"Потратил 500 рублей на продукты\"</i>\n\n"
        "• Кнопка <b>➕ Добавить</b> в меню\n"
        "  Пошаговый ввод с выбором категорий\n\n"
        
        "📊 <b>Просмотр данных:</b>\n"
        "• <b>💰 Доходы</b> — список всех доходов\n"
        "• <b>💸 Расходы</b> — список всех расходов\n"
        "• <b>📊 Статистика</b> — баланс и аналитика\n\n"
        
        "⚙️ <b>Дополнительно:</b>\n"
        "Кнопка <b>📂 Ещё</b> открывает:\n"
        "• 📝 Все транзакции\n"
        "• 📅 Фильтр по периоду\n"
        "• 🏷️ Управление категориями\n"
        "• 📤 Экспорт в Excel\n"
        "• ⚙️ Настройки\n\n"
        
        "✏️ <b>Редактирование:</b>\n"
        "В списках доходов/расходов нажми на кнопку транзакции, "
        "чтобы изменить сумму, категорию или удалить.\n\n"
        
        "💡 <b>Совет:</b> Используй меню внизу экрана для быстрого доступа!"
    )
    
    await message.answer(help_text, parse_mode="HTML")


## Обработчик кнопки "📂 Ещё"
@router.message(F.text == "📂 Ещё")
async def handle_additional_menu(message: Message) -> None:
    """
    Показать дополнительное меню с второстепенными функциями.
    
    :param message: Сообщение от пользователя
    :return: None
    """
    logger.info(f"Пользователь {message.from_user.id} открыл дополнительное меню")
    
    await message.answer(
        "📂 <b>Дополнительные функции</b>\n\n"
        "Выбери нужный раздел:",
        reply_markup=get_additional_menu_keyboard()
    )


## Обработчик кнопки "◀️ Назад"
@router.message(F.text == "◀️ Назад")
async def handle_back_to_main(message: Message) -> None:
    """
    Вернуться в главное меню.
    
    :param message: Сообщение от пользователя
    :return: None
    """
    logger.info(f"Пользователь {message.from_user.id} вернулся в главное меню")
    
    await message.answer(
        "📋 <b>Главное меню</b>\n\n"
        "Используй кнопки ниже для быстрого доступа 👇",
        reply_markup=get_main_reply_keyboard()
    )

