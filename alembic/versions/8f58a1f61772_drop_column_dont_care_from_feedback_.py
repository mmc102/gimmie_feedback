"""Drop column 'dont_care' from 'feedback' table

Revision ID: 8f58a1f61772
Revises: db45d9394e2e
Create Date: 2024-03-20 20:50:41.682716

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8f58a1f61772'
down_revision: Union[str, None] = 'db45d9394e2e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('feedback', 'dont_care')


def downgrade() -> None:
    pass
