"""restore id primary key on prices table

Revision ID: cba229e510e2
Revises: 6106e28312f1
Create Date: 2026-09-12 16:00:06.613248

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cba229e510e2'
down_revision: Union[str, Sequence[str], None] = '6106e28312f1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # The live prices table was missing its `id` column entirely (PK sat on
    # quantity_id instead), out of sync with the Price model, which has
    # always declared a dedicated `id` primary key. Restoring it here;
    # quantity_id keeps a unique constraint so "one price per quantity"
    # still holds (that was the old PK's job).
    op.drop_constraint('prices_pkey', 'prices', type_='primary')
    op.add_column('prices', sa.Column('id', sa.Integer(), sa.Identity(always=False), nullable=False))
    op.create_primary_key('prices_pkey', 'prices', ['id'])
    op.create_unique_constraint('uq_prices_quantity_id', 'prices', ['quantity_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('uq_prices_quantity_id', 'prices', type_='unique')
    op.drop_constraint('prices_pkey', 'prices', type_='primary')
    op.drop_column('prices', 'id')
    op.create_primary_key('prices_pkey', 'prices', ['quantity_id'])
