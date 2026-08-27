"""add custom job fields

Revision ID: f1g2h3i4j5k6
Revises: eaf67013ac11
Create Date: 2026-08-24 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1g2h3i4j5k6'
down_revision: Union[str, None] = 'eaf67013ac11'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add columns for custom job management
    op.add_column('jobs', sa.Column('is_custom', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('jobs', sa.Column('application_url', sa.String(length=1024), nullable=True))
    op.add_column('jobs', sa.Column('badge_status', sa.String(length=50), nullable=True, server_default='live'))
    op.add_column('jobs', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))


def downgrade() -> None:
    # Remove the columns
    op.drop_column('jobs', 'is_active')
    op.drop_column('jobs', 'badge_status')
    op.drop_column('jobs', 'application_url')
    op.drop_column('jobs', 'is_custom')
