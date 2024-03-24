"""add private event field

Revision ID: 47732dff28b4
Revises: b4380844ac39
Create Date: 2024-03-23 20:31:17.590270

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '47732dff28b4'
down_revision: Union[str, None] = 'b4380844ac39'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('events', sa.Column('private', sa.Boolean(), nullable=False, server_default="false"))

def downgrade() -> None:
    op.drop_column('events', 'private')

