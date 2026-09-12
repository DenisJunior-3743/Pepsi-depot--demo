"""record personnel depot_id and email columns

Revision ID: f658f707e56f
Revises: cba229e510e2
Create Date: 2026-09-12 16:49:04.425575

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f658f707e56f'
down_revision: Union[str, Sequence[str], None] = 'cba229e510e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # depot_id and email were already added to the live personnel table by
    # hand (no migration tooling was used at the time) - using IF NOT EXISTS
    # so this is safe to run regardless, and brings Alembic's history in
    # sync with what's actually live.
    op.execute("ALTER TABLE personnel ADD COLUMN IF NOT EXISTS depot_id INTEGER REFERENCES depots(id)")
    op.execute("ALTER TABLE personnel ADD COLUMN IF NOT EXISTS email VARCHAR(255)")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("ALTER TABLE personnel DROP COLUMN IF EXISTS email")
    op.execute("ALTER TABLE personnel DROP COLUMN IF EXISTS depot_id")
