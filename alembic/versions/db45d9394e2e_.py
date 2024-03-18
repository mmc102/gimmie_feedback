"""empty message

Revision ID: db45d9394e2e
Revises: 
Create Date: 2024-03-17 18:47:59.793962

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'db45d9394e2e'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('events', sa.Column('password', sa.String(), nullable=False, server_default=''))

def downgrade() -> None:
    op.drop_column('events', 'password')
