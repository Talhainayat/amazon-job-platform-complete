"""add official job links"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "g7h8i9j0k1l2"
down_revision: Union[str, None] = "0ba9aba22bf0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("jobs", sa.Column("external_url", sa.String(length=1024), nullable=True))
    op.add_column("jobs", sa.Column("is_official_link", sa.Boolean(), nullable=False, server_default=sa.true()))


def downgrade() -> None:
    op.drop_column("jobs", "is_official_link")
    op.drop_column("jobs", "external_url")