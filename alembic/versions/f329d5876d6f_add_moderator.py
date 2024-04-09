"""add moderator

Revision ID: f329d5876d6f
Revises: c22d53088734
Create Date: 2024-04-08 17:54:00.954956

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f329d5876d6f'
down_revision: Union[str, None] = 'c22d53088734'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('admin', sa.Boolean(), nullable=False, server_default="false"))


def downgrade() -> None:
    op.drop_column('users', 'admin')
