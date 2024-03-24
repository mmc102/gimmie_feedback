"""add time to event

Revision ID: 8bf40ee0bcb9
Revises: 8607aa771fed
Create Date: 2024-03-23 21:32:39.309251

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8bf40ee0bcb9'
down_revision: Union[str, None] = '8607aa771fed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('events', sa.Column('time', sa.String(), nullable=False, server_default='19:00'))

def downgrade() -> None:
    op.drop_column('events', 'time')




