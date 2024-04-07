"""add user_id to events

Revision ID: c22d53088734
Revises: 1e158762948d
Create Date: 2024-04-07 08:49:31.280894

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c22d53088734'
down_revision: Union[str, None] = '1e158762948d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: Add the user_id column to the events table
    op.add_column('events',
                  sa.Column('user_id', sa.String(length=36)))

    # Step 2: Populate the user_id column with the first user's ID
    op.execute("UPDATE events SET user_id = (SELECT id FROM users LIMIT 1)")

    # Step 3: Create a foreign key constraint on the user_id column
    op.create_foreign_key('fk_user_id',
                          'events',
                          'users',
                          ['user_id'],
                          ['id'],
                          ondelete='CASCADE')


def downgrade() -> None:
    pass
