"""add event location

Revision ID: b4380844ac39
Revises: 8f58a1f61772
Create Date: 2024-03-21 13:46:07.710643

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b4380844ac39'
down_revision: Union[str, None] = '8f58a1f61772'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('events', sa.Column('location', sa.String(), nullable=False, server_default=''))

def downgrade() -> None:
    op.drop_column('events', 'location')

