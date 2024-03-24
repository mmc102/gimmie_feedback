"""update pkey on events

Revision ID: 35f5a06d872a
Revises: eaea10c801c4
Create Date: 2024-03-23 20:43:12.883555

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = '35f5a06d872a'
down_revision: Union[str, None] = 'eaea10c801c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('presentations_event_id_fkey', 'presentations', type_='foreignkey')

    op.add_column('presentations', sa.Column('event_uuid', UUID(as_uuid=True), nullable=True))
    op.execute(
        """
        UPDATE presentations AS p
        SET event_uuid = e.uuid
        FROM events AS e
        WHERE p.event_id = e.id
        """
    )

    op.drop_column('presentations', 'event_id')
    op.alter_column('presentations', 'event_uuid', new_column_name='event_id')

    op.create_foreign_key('presentations_event_uuid_fkey', 'presentations', 'events', ['event_id'], ['uuid'], ondelete='CASCADE')


def downgrade() -> None:
    pass


