"""
Модель категории доходов и расходов.

Хранит категории для классификации транзакций пользователя.
"""

from typing import List, TYPE_CHECKING
from enum import Enum as PyEnum
from sqlalchemy import String, Boolean, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .user import User
    from .transaction import Transaction


## Типы категорий
class CategoryType(str, PyEnum):
    """
    Перечисление типов категорий.
    
    :cvar INCOME: Категория доходов
    :cvar EXPENSE: Категория расходов
    """
    
    INCOME = "income"
    EXPENSE = "expense"


## Модель категории
class Category(Base, TimestampMixin):
    """
    Модель категории транзакций.
    
    Категории могут быть предустановленными (системными) или пользовательскими.
    Предустановленные категории создаются при первом запуске и общие для всех,
    пользовательские - создаются конкретным пользователем.
    
    :ivar id: Первичный ключ (автоинкремент)
    :ivar name: Название категории
    :ivar type: Тип категории (доход/расход)
    :ivar emoji: Эмодзи для визуального представления
    :ivar is_default: Флаг предустановленной категории
    :ivar user_id: ID пользователя (NULL для предустановленных)
    :ivar user: Связь с пользователем
    :ivar transactions: Список транзакций в этой категории
    """
    
    __tablename__ = "categories"
    __table_args__ = {"comment": "Категории доходов и расходов"}
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Название категории"
    )
    
    type: Mapped[CategoryType] = mapped_column(
        Enum(CategoryType, name="category_type"),
        nullable=False,
        index=True,
        comment="Тип категории (доход/расход)"
    )
    
    emoji: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="📝",
        comment="Эмодзи категории"
    )
    
    is_default: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
        comment="Предустановленная категория (системная)"
    )
    
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="ID пользователя (NULL для предустановленных)"
    )
    
    user: Mapped["User"] = relationship(
        "User",
        back_populates="categories"
    )
    
    transactions: Mapped[List["Transaction"]] = relationship(
        "Transaction",
        back_populates="category",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        """Строковое представление категории."""
        return f"<Category(id={self.id}, name={self.name}, type={self.type}, is_default={self.is_default})>"

