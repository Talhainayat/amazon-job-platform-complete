"""merge_migration_heads

Revision ID: 0ba9aba22bf0
Revises: e6f7a8b9c0d1, f1g2h3i4j5k6
Create Date: 2026-08-24 17:20:18.399899

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0ba9aba22bf0'
down_revision: Union[str, None] = ('e6f7a8b9c0d1', 'f1g2h3i4j5k6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
