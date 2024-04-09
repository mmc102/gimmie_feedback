"""add password

Revision ID: 8305b5f9d956
Revises: f329d5876d6f
Create Date: 2024-04-08 17:59:56.584077

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8305b5f9d956'
down_revision: Union[str, None] = 'f329d5876d6f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('password', sa.String(), nullable=True, server_default="null"))

def downgrade() -> None:
    op.drop_column('users', 'password')
