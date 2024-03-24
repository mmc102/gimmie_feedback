"""rename column in events

Revision ID: 8607aa771fed
Revises: 35f5a06d872a
Create Date: 2024-03-23 21:02:16.240423

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8607aa771fed'
down_revision: Union[str, None] = '35f5a06d872a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # drop primary key on events.id
    # drop events.id
    # rename events.uuid to events.id
    # reestablish the primary key on events.uuid
    op.drop_constraint('events_pkey', 'events', type_='primary')
    op.drop_column('events', 'id')
    op.alter_column('events', 'uuid', new_column_name='id')
    op.create_primary_key('events_pkey', 'events', ['id'])


def downgrade() -> None:
    pass
