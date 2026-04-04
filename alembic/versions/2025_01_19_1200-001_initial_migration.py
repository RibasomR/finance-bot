"""Initial complete migration with all tables, indexes and enum types

Revision ID: 001
Revises: 
Create Date: 2025-01-19 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

## Import Python Enum types for proper enum handling
from bot.models.category import CategoryType
from bot.models.transaction import TransactionType


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Apply database changes.
    
    Creates all tables, enum types, indexes and constraints for the finance bot.
    Includes timezone-aware timestamps and composite indexes for optimization.
    """
    
    ## Import required SQLAlchemy utilities
    from sqlalchemy import inspect
    
    ## Get database connection
    bind = op.get_bind()
    
    ## Check if tables already exist
    inspector = inspect(bind)
    existing_tables = inspector.get_table_names()
    
    ## Create users table with all fields
    if 'users' not in existing_tables:
        op.create_table(
            'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('username', sa.String(255), nullable=True),
        sa.Column('first_name', sa.String(255), nullable=False),
        sa.Column('last_name', sa.String(255), nullable=True),
        sa.Column('max_transaction_limit', sa.Integer(), nullable=True, comment='Personal transaction limit (in rubles)'),
        sa.Column('monthly_limit', sa.Integer(), nullable=True, comment='Monthly spending limit (in rubles)'),
        sa.Column(
            'created_at',
            sa.TIMESTAMP(timezone=True) if bind.dialect.name == 'postgresql' else sa.DateTime(),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            nullable=False
        ),
        sa.Column(
            'updated_at',
            sa.TIMESTAMP(timezone=True) if bind.dialect.name == 'postgresql' else sa.DateTime(),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            nullable=False
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_users')),
        sa.UniqueConstraint('telegram_id', name=op.f('uq_users_telegram_id')),
            comment='Bot users'
        )
        op.create_index(op.f('ix_users_telegram_id'), 'users', ['telegram_id'], unique=False)
    
    ## Create categories table
    if 'categories' not in existing_tables:
        op.create_table(
            'categories',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('type', sa.Enum(CategoryType, name='category_type'), nullable=False),
        sa.Column('emoji', sa.String(10), nullable=False, server_default='📝'),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column(
            'created_at',
            sa.TIMESTAMP(timezone=True) if bind.dialect.name == 'postgresql' else sa.DateTime(),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            nullable=False
        ),
        sa.Column(
            'updated_at',
            sa.TIMESTAMP(timezone=True) if bind.dialect.name == 'postgresql' else sa.DateTime(),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            nullable=False
        ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_categories_user_id_users'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_categories')),
            comment='Income and expense categories'
        )
        op.create_index(op.f('ix_categories_type'), 'categories', ['type'], unique=False)
        op.create_index(op.f('ix_categories_is_default'), 'categories', ['is_default'], unique=False)
        op.create_index(op.f('ix_categories_user_id'), 'categories', ['user_id'], unique=False)
        
        ## Composite index for category filtering by user and type
        op.create_index(
            'ix_categories_user_type',
            'categories',
            ['user_id', 'type'],
            unique=False
        )
    
    ## Create transactions table
    if 'transactions' not in existing_tables:
        op.create_table(
            'transactions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.Enum(TransactionType, name='transaction_type'), nullable=False),
        sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column(
            'created_at',
            sa.TIMESTAMP(timezone=True) if bind.dialect.name == 'postgresql' else sa.DateTime(),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            nullable=False
        ),
        sa.Column(
            'updated_at',
            sa.TIMESTAMP(timezone=True) if bind.dialect.name == 'postgresql' else sa.DateTime(),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            nullable=False
        ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_transactions_user_id_users'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], name=op.f('fk_transactions_category_id_categories'), ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_transactions')),
            comment='User financial transactions'
        )
        
        ## Single column indexes
        op.create_index(op.f('ix_transactions_user_id'), 'transactions', ['user_id'], unique=False)
        op.create_index(op.f('ix_transactions_type'), 'transactions', ['type'], unique=False)
        op.create_index(op.f('ix_transactions_category_id'), 'transactions', ['category_id'], unique=False)
        op.create_index(op.f('ix_transactions_created_at'), 'transactions', ['created_at'], unique=False)
        
        ## Composite indexes for optimization
        ## Filter transactions by user and type
        op.create_index(
            'ix_transactions_user_type',
            'transactions',
            ['user_id', 'type'],
            unique=False
        )
        
        ## Filter transactions by user and date
        op.create_index(
            'ix_transactions_user_created',
            'transactions',
            ['user_id', 'created_at'],
            unique=False
        )
        
        ## Category statistics for period
        op.create_index(
            'ix_transactions_category_created',
            'transactions',
            ['category_id', 'created_at'],
            unique=False
        )


def downgrade() -> None:
    """
    Rollback database changes.
    
    Drops all tables, indexes and enum types in reverse order.
    """
    
    ## Drop transactions table with all indexes
    op.drop_index('ix_transactions_category_created', table_name='transactions')
    op.drop_index('ix_transactions_user_created', table_name='transactions')
    op.drop_index('ix_transactions_user_type', table_name='transactions')
    op.drop_index(op.f('ix_transactions_created_at'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_category_id'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_type'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_user_id'), table_name='transactions')
    op.drop_table('transactions')
    
    ## Drop categories table with all indexes
    op.drop_index('ix_categories_user_type', table_name='categories')
    op.drop_index(op.f('ix_categories_user_id'), table_name='categories')
    op.drop_index(op.f('ix_categories_is_default'), table_name='categories')
    op.drop_index(op.f('ix_categories_type'), table_name='categories')
    op.drop_table('categories')
    
    ## Drop users table with all indexes
    op.drop_index(op.f('ix_users_telegram_id'), table_name='users')
    op.drop_table('users')
    
    ## Drop ENUM types (PostgreSQL only)
    ## These will be automatically dropped by SQLAlchemy when tables are dropped
    ## but we explicitly drop them to ensure cleanup
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        from sqlalchemy import text
        op.execute(text('DROP TYPE IF EXISTS transaction_type CASCADE'))
        op.execute(text('DROP TYPE IF EXISTS category_type CASCADE'))
