"""add sorted order to presentations

Revision ID: 1e158762948d
Revises: e03410eafc14
Create Date: 2024-04-04 07:28:03.825192

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1e158762948d'
down_revision: Union[str, None] = 'e03410eafc14'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('presentations', sa.Column('order', sa.Integer ,server_default='1'))


def downgrade() -> None:

    op.drop_column('presentations', 'order')
