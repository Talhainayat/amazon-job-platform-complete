"""add managed site feeds"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision: str = "e6f7a8b9c0d1"
down_revision: Union[str, None] = "d5e6f7a8b9c0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    connection = op.get_bind()
    if "managed_sites" not in inspect(connection).get_table_names():
        op.create_table("managed_sites", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(255), nullable=False), sa.Column("postal_code", sa.String(20)), sa.Column("portal_url", sa.String(1024)), sa.Column("feed_enabled", sa.Boolean(), nullable=False, server_default=sa.true()), sa.Column("available_slots", sa.Integer(), nullable=False, server_default="0"), sa.Column("created_at", sa.DateTime(), nullable=False))
    if "ix_managed_sites_id" not in {index["name"] for index in inspect(connection).get_indexes("managed_sites") }:
        op.create_index("ix_managed_sites_id", "managed_sites", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_managed_sites_id", table_name="managed_sites")
    op.drop_table("managed_sites")