"""add currency to transactions

Revision ID: 002_add_currency
Revises: 001_initial_migration
Create Date: 2025-11-14 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Добавить поле currency в таблицу transactions.
    
    Добавляет колонку currency (VARCHAR(3)) со значением по умолчанию 'RUB'.
    """
    # Добавление колонки currency
    op.add_column('transactions', sa.Column('currency', sa.String(length=3), server_default='RUB', nullable=False, comment='Валюта транзакции (RUB, USD)'))


def downgrade() -> None:
    """
    Удалить поле currency из таблицы transactions.
    """
    # Удаление колонки currency
    op.drop_column('transactions', 'currency')

