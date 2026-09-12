"""add supply history status workflow

Revision ID: 6106e28312f1
Revises: 19a4d7b3e882
Create Date: 2026-09-12 15:33:05.708650

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6106e28312f1'
down_revision: Union[str, Sequence[str], None] = '19a4d7b3e882'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


supply_status_enum = sa.Enum('pending', 'received', 'rejected', name='supplystatus')


def upgrade() -> None:
    """Upgrade schema."""
    # Orphaned leftover from an earlier, abandoned factory design (the old
    # supplies/supply_items tables, since replaced by supply_history) — no
    # table or column references it, but its name collides with the new
    # SupplyStatus enum below.
    op.execute("DROP TYPE IF EXISTS supplystatus")
    supply_status_enum.create(op.get_bind())

    op.add_column(
        'supply_history',
        sa.Column('status', supply_status_enum, nullable=False, server_default='pending'),
    )
    op.add_column('supply_history', sa.Column('rejection_reason', sa.String(), nullable=True))
    op.add_column(
        'supply_history',
        sa.Column('created_date', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('supply_history', 'created_date')
    op.drop_column('supply_history', 'rejection_reason')
    op.drop_column('supply_history', 'status')
    op.execute("DROP TYPE IF EXISTS supplystatus")
