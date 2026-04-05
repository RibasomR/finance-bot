"""
Система локализации бота.

Предоставляет функцию t() для получения переведённых строк
на основе языка пользователя.
"""

from typing import Any
from bot.locales.ru import STRINGS as RU_STRINGS
from bot.locales.en import STRINGS as EN_STRINGS

LOCALES = {
    "ru": RU_STRINGS,
    "en": EN_STRINGS,
}

# Маппинг русских названий категорий -> ключи локализации
CATEGORY_NAME_TO_KEY = {
    # Расходы
    "Продукты": "cat_groceries",
    "Дом и ЖКХ": "cat_home",
    "Транспорт": "cat_transport",
    "Здоровье": "cat_health",
    "Одежда": "cat_clothing",
    "Развлечения": "cat_entertainment",
    "Рестораны и кафе": "cat_restaurants",
    "Связь и интернет": "cat_communication",
    "Аптека": "cat_pharmacy",
    "Другое": "cat_other",
    # Доходы
    "Зарплата": "cat_salary",
    "Фриланс": "cat_freelance",
    "Подарок": "cat_gift",
    "Инвестиции": "cat_investments",
    # EN names -> keys (для обратного маппинга)
    "Groceries": "cat_groceries",
    "Home & Utilities": "cat_home",
    "Transport": "cat_transport",
    "Health": "cat_health",
    "Clothing": "cat_clothing",
    "Entertainment": "cat_entertainment",
    "Restaurants & Cafes": "cat_restaurants",
    "Phone & Internet": "cat_communication",
    "Pharmacy": "cat_pharmacy",
    "Other": "cat_other",
    "Salary": "cat_salary",
    "Freelance": "cat_freelance",
    "Gift": "cat_gift",
    "Investments": "cat_investments",
}


def t(key: str, lang: str = "ru", **kwargs: Any) -> Any:
    """
    Получить переведённую строку по ключу и языку.

    Поддерживает подстановку переменных через kwargs.
    Если ключ не найден в запрашиваемом языке, fallback на русский.
    Если и в русском нет — возвращает сам ключ.

    :param key: Ключ строки в словаре локализации
    :param lang: Код языка ('ru' или 'en')
    :param kwargs: Именованные аргументы для подстановки в строку
    :return: Переведённая строка или значение (для списков)

    Example:
        >>> t("welcome", "ru", name="Иван")
        "Привет, Иван!..."
        >>> t("btn_income", "en")
        "Income"
    """
    strings = LOCALES.get(lang, LOCALES["ru"])
    value = strings.get(key)

    if value is None:
        # Fallback на русский
        value = LOCALES["ru"].get(key)

    if value is None:
        return key

    # Для не-строковых типов (list, etc.) возвращаем как есть
    if not isinstance(value, str):
        return value

    if kwargs:
        try:
            return value.format(**kwargs)
        except (KeyError, IndexError):
            return value

    return value


def translate_category_name(name: str, lang: str) -> str:
    """
    Перевести название категории на язык пользователя.

    Если категория — дефолтная (есть в маппинге), переводит.
    Если пользовательская — возвращает как есть.

    :param name: Название категории (как хранится в БД)
    :param lang: Код языка
    :return: Переведённое название
    """
    key = CATEGORY_NAME_TO_KEY.get(name)
    if key:
        return t(key, lang)
    return name


__all__ = ["t", "translate_category_name", "CATEGORY_NAME_TO_KEY", "LOCALES"]
