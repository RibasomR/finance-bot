"""add language to users

Revision ID: 003_add_language
Revises: 002
Create Date: 2026-04-05 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Добавить поле language в таблицу users.

    Добавляет колонку language (VARCHAR(5)) со значением по умолчанию 'ru'.
    Все существующие пользователи получат язык 'ru'.
    """
    op.add_column('users', sa.Column(
        'language',
        sa.String(length=5),
        server_default='ru',
        nullable=False,
        comment='Язык интерфейса пользователя (ru/en)'
    ))


def downgrade() -> None:
    """
    Удалить поле language из таблицы users.
    """
    op.drop_column('users', 'language')
