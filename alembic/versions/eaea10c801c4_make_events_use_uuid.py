"""make events use uuid

Revision ID: eaea10c801c4
Revises: 47732dff28b4
Create Date: 2024-03-23 20:35:59.005928

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = 'eaea10c801c4'
down_revision: Union[str, None] = '47732dff28b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')

    op.add_column('events', sa.Column('uuid', UUID(as_uuid=True), nullable=False, unique=True, server_default=sa.text('uuid_generate_v4()')))

    op.execute('UPDATE events SET uuid = uuid_generate_v4()')


def downgrade():
    pass
