"""add approved flag to event

Revision ID: e03410eafc14
Revises: 8bf40ee0bcb9
Create Date: 2024-04-03 13:14:03.246064

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e03410eafc14'
down_revision: Union[str, None] = '8bf40ee0bcb9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('events', sa.Column('approved', sa.Boolean(), nullable=False, server_default="false"))

    op.add_column('users', sa.Column('newsletter', sa.Boolean(), nullable=False, server_default="false"))



def downgrade() -> None:
    op.drop_column('events', 'approved')
    op.drop_column('users', 'newsletter')
