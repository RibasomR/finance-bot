"""
Обработчики общих команд бота.

Содержит handlers для команд /start и /help,
включая выбор языка при первом запуске.
"""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from loguru import logger
from sqlalchemy import select

from bot.keyboards.reply_keyboards import get_main_reply_keyboard, get_additional_menu_keyboard
from bot.services.database import get_or_create_user
from bot.models import get_session, User
from bot.locales import t

router = Router(name="common")


## Клавиатура выбора языка
def get_language_keyboard() -> InlineKeyboardMarkup:
    """
    Создать inline-клавиатуру для выбора языка.

    :return: Inline-клавиатура с кнопками выбора языка
    """
    keyboard = [
        [
            InlineKeyboardButton(text="\U0001f1f7\U0001f1fa Русский", callback_data="lang:ru"),
            InlineKeyboardButton(text="\U0001f1ec\U0001f1e7 English", callback_data="lang:en"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


## Обработчик команды /start
@router.message(Command("start"))
async def cmd_start(message: Message, lang: str = "ru") -> None:
    """
    Обработчик команды /start.

    При первом запуске (пользователя нет в БД) показывает выбор языка.
    При повторном /start сразу показывает главное меню.

    :param message: Объект сообщения от пользователя
    :param lang: Язык пользователя из middleware
    :return: None
    """
    user_tg = message.from_user
    logger.info(f"Пользователь {user_tg.id} (@{user_tg.username}) запустил бота")

    # Проверяем, существует ли пользователь в БД
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_tg.id)
        )
        existing_user = result.scalar_one_or_none()

    if not existing_user:
        # Первый запуск — показываем выбор языка
        await message.answer(
            "Please select your language:",
            reply_markup=get_language_keyboard()
        )
        return

    # Повторный /start — показываем главное меню
    welcome_text = (
        f"\U0001f44b {t('welcome', lang, name=user_tg.first_name)}"
    )

    await message.answer(
        welcome_text,
        parse_mode="HTML",
        reply_markup=get_main_reply_keyboard(lang)
    )


## Обработчик выбора языка (первый запуск и смена языка)
@router.callback_query(F.data.startswith("lang:"))
async def process_language_selection(callback: CallbackQuery) -> None:
    """
    Обработка выбора языка.

    При первом запуске — создаёт пользователя с выбранным языком.
    При смене языка — обновляет поле в БД.

    :param callback: Callback query от пользователя
    :return: None
    """
    selected_lang = callback.data.split(":")[1]
    user_tg = callback.from_user

    # Проверяем, есть ли пользователь в БД
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_tg.id)
        )
        existing_user = result.scalar_one_or_none()

    if not existing_user:
        # Первый запуск — создаём пользователя с выбранным языком
        user = await get_or_create_user(
            telegram_id=user_tg.id,
            username=user_tg.username,
            first_name=user_tg.first_name,
            last_name=user_tg.last_name,
        )
        # Устанавливаем язык
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == user_tg.id)
            )
            db_user = result.scalar_one_or_none()
            if db_user:
                db_user.language = selected_lang
                await session.commit()

        logger.info(f"Новый пользователь {user_tg.id} выбрал язык: {selected_lang}")

        # Показываем приветствие на выбранном языке
        welcome_text = (
            f"\U0001f44b {t('welcome', selected_lang, name=user_tg.first_name)}"
        )

        await callback.message.edit_text(
            welcome_text,
            parse_mode="HTML"
        )

        await callback.message.answer(
            f"\U0001f4cb <b>{t('main_menu_title', selected_lang)}</b>\n\n"
            f"{t('main_menu_subtitle', selected_lang)}",
            reply_markup=get_main_reply_keyboard(selected_lang)
        )
    else:
        # Смена языка из настроек
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == user_tg.id)
            )
            db_user = result.scalar_one_or_none()
            if db_user:
                db_user.language = selected_lang
                await session.commit()

        logger.info(f"Пользователь {user_tg.id} сменил язык на: {selected_lang}")

        await callback.message.edit_text(
            f"\u2705 {t('language_changed', selected_lang)}"
        )

        # Обновляем reply-клавиатуру
        await callback.message.answer(
            f"\U0001f4cb <b>{t('main_menu_title', selected_lang)}</b>\n\n"
            f"{t('main_menu_subtitle', selected_lang)}",
            reply_markup=get_main_reply_keyboard(selected_lang)
        )

    await callback.answer()


## Обработчик команды /help
@router.message(Command("help"))
async def cmd_help(message: Message, lang: str = "ru") -> None:
    """
    Обработчик команды /help.

    :param message: Объект сообщения от пользователя
    :param lang: Язык пользователя из middleware
    :return: None
    """
    logger.info(f"Пользователь {message.from_user.id} запросил помощь")

    help_text = (
        f"\U0001f4da <b>{t('help_title', lang)}</b>\n\n"
        f"{t('help_text', lang)}"
    )

    await message.answer(help_text, parse_mode="HTML")


## Обработчик кнопки "Ещё"
@router.message(F.text.in_({"📂 Ещё", "📂 More"}))
async def handle_additional_menu(message: Message, lang: str = "ru") -> None:
    """
    Показать дополнительное меню с второстепенными функциями.

    :param message: Сообщение от пользователя
    :param lang: Язык пользователя из middleware
    :return: None
    """
    logger.info(f"Пользователь {message.from_user.id} открыл дополнительное меню")

    await message.answer(
        f"\U0001f4c2 <b>{t('additional_menu_title', lang)}</b>\n\n"
        f"{t('additional_menu_subtitle', lang)}",
        reply_markup=get_additional_menu_keyboard(lang)
    )


## Обработчик кнопки "Назад"
@router.message(F.text.in_({"◀️ Назад", "◀️ Back"}))
async def handle_back_to_main(message: Message, lang: str = "ru") -> None:
    """
    Вернуться в главное меню.

    :param message: Сообщение от пользователя
    :param lang: Язык пользователя из middleware
    :return: None
    """
    logger.info(f"Пользователь {message.from_user.id} вернулся в главное меню")

    await message.answer(
        f"\U0001f4cb <b>{t('main_menu_title', lang)}</b>\n\n"
        f"{t('main_menu_subtitle', lang)} \U0001f447",
        reply_markup=get_main_reply_keyboard(lang)
    )
