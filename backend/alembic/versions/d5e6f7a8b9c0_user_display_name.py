"""add user display name

Revision ID: d5e6f7a8b9c0
Revises: c4f1a2b3d4e5
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision: str = "d5e6f7a8b9c0"
down_revision: Union[str, None] = "c4f1a2b3d4e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    if "name" not in {column["name"] for column in inspect(op.get_bind()).get_columns("users") }:
        op.add_column("users", sa.Column("name", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "name")