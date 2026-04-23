"""add_daily_limit_and_introduced_date

Revision ID: f3a1d9c2b847
Revises: d83e8efcb0c1
Create Date: 2026-04-22 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f3a1d9c2b847'
down_revision: Union[str, None] = 'd83e8efcb0c1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('daily_new_limit', sa.Integer(), nullable=False, server_default='20'))
    op.add_column('reviews', sa.Column('introduced_date', sa.Date(), nullable=True))
    op.create_index('ix_reviews_introduced_date', 'reviews', ['introduced_date'])


def downgrade() -> None:
    op.drop_index('ix_reviews_introduced_date', table_name='reviews')
    op.drop_column('reviews', 'introduced_date')
    op.drop_column('users', 'daily_new_limit')
