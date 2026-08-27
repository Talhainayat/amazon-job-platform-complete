"""add public contact inquiries

Revision ID: c4f1a2b3d4e5
Revises: b7c2d91e4a10
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision: str = "c4f1a2b3d4e5"
down_revision: Union[str, None] = "b7c2d91e4a10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    connection = op.get_bind()
    if "contact_inquiries" not in inspect(connection).get_table_names():
        op.create_table(
            "contact_inquiries",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("email", sa.String(length=255), nullable=False),
            sa.Column("phone", sa.String(length=50), nullable=True),
            sa.Column("message", sa.Text(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
    if "ix_contact_inquiries_id" not in {index["name"] for index in inspect(connection).get_indexes("contact_inquiries") }:
        op.create_index("ix_contact_inquiries_id", "contact_inquiries", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_contact_inquiries_id", table_name="contact_inquiries")
    op.drop_table("contact_inquiries")