"""platform mvp fields

Revision ID: b7c2d91e4a10
Revises: eaf67013ac11
Create Date: 2026-08-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b7c2d91e4a10"
down_revision: Union[str, None] = "eaf67013ac11"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _add_column(table: str, column: sa.Column) -> None:
    with op.batch_alter_table(table) as batch:
        batch.add_column(column)


def upgrade() -> None:
    _add_column("jobs", sa.Column("company", sa.String(length=255), nullable=True))
    _add_column("jobs", sa.Column("requirements", sa.Text(), nullable=True))
    _add_column("jobs", sa.Column("city", sa.String(length=255), nullable=True))
    _add_column("jobs", sa.Column("province", sa.String(length=100), nullable=True))
    _add_column("jobs", sa.Column("postal_code", sa.String(length=20), nullable=True))
    _add_column("jobs", sa.Column("latitude", sa.Float(), nullable=True))
    _add_column("jobs", sa.Column("longitude", sa.Float(), nullable=True))
    _add_column("jobs", sa.Column("skills", sa.JSON(), nullable=True))
    _add_column("jobs", sa.Column("years_experience", sa.Integer(), nullable=True))
    _add_column("jobs", sa.Column("openings", sa.Integer(), nullable=True))
    _add_column("jobs", sa.Column("pay_min", sa.Float(), nullable=True))
    _add_column("jobs", sa.Column("pay_max", sa.Float(), nullable=True))
    _add_column("jobs", sa.Column("pay_period", sa.String(length=30), nullable=True))
    _add_column("jobs", sa.Column("application_deadline", sa.DateTime(), nullable=True))

    _add_column("candidates", sa.Column("city", sa.String(length=255), nullable=True))
    _add_column("candidates", sa.Column("province", sa.String(length=100), nullable=True))
    _add_column("candidates", sa.Column("latitude", sa.Float(), nullable=True))
    _add_column("candidates", sa.Column("longitude", sa.Float(), nullable=True))
    _add_column("candidates", sa.Column("skills", sa.JSON(), nullable=True))
    _add_column("candidates", sa.Column("years_experience", sa.Integer(), nullable=True))
    _add_column("candidates", sa.Column("experience", sa.Text(), nullable=True))
    _add_column("candidates", sa.Column("education", sa.Text(), nullable=True))
    _add_column("candidates", sa.Column("availability", sa.String(length=100), nullable=True))
    _add_column("candidates", sa.Column("has_vehicle", sa.Boolean(), nullable=True))
    _add_column("candidates", sa.Column("resume_path", sa.String(length=1024), nullable=True))
    _add_column("candidates", sa.Column("resume_filename", sa.String(length=255), nullable=True))

    _add_column("candidate_preferences", sa.Column("maximum_pay", sa.Float(), nullable=True))
    _add_column("candidate_preferences", sa.Column("availability", sa.String(length=100), nullable=True))
    _add_column("candidate_preferences", sa.Column("has_vehicle", sa.Boolean(), nullable=True))
    _add_column("candidate_preferences", sa.Column("years_experience", sa.Integer(), nullable=True))

    _add_column("matches", sa.Column("explanation", sa.JSON(), nullable=True))
    _add_column("matches", sa.Column("distance_km", sa.Float(), nullable=True))
    _add_column("matches", sa.Column("distance_known", sa.Boolean(), nullable=True))

    _add_column("notifications", sa.Column("user_id", sa.Integer(), nullable=True))
    _add_column("notifications", sa.Column("application_id", sa.Integer(), nullable=True))
    _add_column("notifications", sa.Column("title", sa.String(length=255), nullable=True))
    _add_column("notifications", sa.Column("notification_type", sa.String(length=80), nullable=True))
    _add_column("notifications", sa.Column("is_read", sa.Boolean(), nullable=True))


def downgrade() -> None:
    pass
