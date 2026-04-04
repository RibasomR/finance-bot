"""
Модель пользователя бота.

Хранит информацию о пользователях Telegram, которые используют бота.
"""

from typing import List, TYPE_CHECKING
from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .category import Category
    from .transaction import Transaction


## Модель пользователя
class User(Base, TimestampMixin):
    """
    Модель пользователя бота.
    
    Хранит базовую информацию о пользователе Telegram.
    Связана с категориями и транзакциями через внешние ключи.
    
    :ivar id: Первичный ключ (автоинкремент)
    :ivar telegram_id: Уникальный ID пользователя в Telegram
    :ivar username: Имя пользователя в Telegram (опционально)
    :ivar first_name: Имя пользователя
    :ivar last_name: Фамилия пользователя (опционально)
    :ivar max_transaction_limit: Персональный лимит максимальной транзакции
    :ivar monthly_limit: Месячный лимит трат (в рублях)
    :ivar categories: Список пользовательских категорий
    :ivar transactions: Список всех транзакций пользователя
    """
    
    __tablename__ = "users"
    __table_args__ = {"comment": "Пользователи бота"}
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        nullable=False,
        index=True,
        comment="ID пользователя в Telegram"
    )
    
    username: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Username в Telegram"
    )
    
    first_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Имя пользователя"
    )
    
    last_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Фамилия пользователя"
    )
    
    max_transaction_limit: Mapped[int | None] = mapped_column(
        nullable=True,
        comment="Персональный лимит максимальной транзакции (в рублях)"
    )
    
    monthly_limit: Mapped[int | None] = mapped_column(
        nullable=True,
        comment="Месячный лимит трат (в рублях)"
    )
    
    categories: Mapped[List["Category"]] = relationship(
        "Category",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    transactions: Mapped[List["Transaction"]] = relationship(
        "Transaction",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        """Строковое представление пользователя."""
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, username={self.username})>"

