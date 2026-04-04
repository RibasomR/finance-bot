"""
Модель транзакции (доход или расход).

Хранит информацию о финансовых операциях пользователя.
"""

from typing import TYPE_CHECKING
from enum import Enum as PyEnum
from decimal import Decimal
from sqlalchemy import String, Numeric, ForeignKey, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .user import User
    from .category import Category


## Типы транзакций
class TransactionType(str, PyEnum):
    """
    Перечисление типов транзакций.
    
    :cvar INCOME: Доход
    :cvar EXPENSE: Расход
    """
    
    INCOME = "income"
    EXPENSE = "expense"


## Модель транзакции
class Transaction(Base, TimestampMixin):
    """
    Модель финансовой транзакции.
    
    Представляет одну финансовую операцию (доход или расход) пользователя.
    Связана с пользователем и категорией через внешние ключи.
    
    :ivar id: Первичный ключ (автоинкремент)
    :ivar user_id: ID пользователя, которому принадлежит транзакция
    :ivar type: Тип транзакции (доход/расход)
    :ivar amount: Сумма транзакции (с копейками)
    :ivar currency: Валюта транзакции (RUB, USD)
    :ivar category_id: ID категории транзакции
    :ivar description: Описание/комментарий к транзакции (опционально)
    :ivar user: Связь с пользователем
    :ivar category: Связь с категорией
    """
    
    __tablename__ = "transactions"
    __table_args__ = {"comment": "Финансовые транзакции пользователей"}
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID пользователя"
    )
    
    type: Mapped[TransactionType] = mapped_column(
        Enum(TransactionType, name="transaction_type"),
        nullable=False,
        index=True,
        comment="Тип транзакции (доход/расход)"
    )
    
    amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=15, scale=2),
        nullable=False,
        comment="Сумма транзакции"
    )
    
    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="RUB",
        server_default="RUB",
        comment="Валюта транзакции (RUB, USD)"
    )
    
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="ID категории"
    )
    
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Описание транзакции"
    )
    
    user: Mapped["User"] = relationship(
        "User",
        back_populates="transactions"
    )
    
    category: Mapped["Category"] = relationship(
        "Category",
        back_populates="transactions"
    )
    
    def __repr__(self) -> str:
        """Строковое представление транзакции."""
        return f"<Transaction(id={self.id}, type={self.type}, amount={self.amount}, user_id={self.user_id})>"

