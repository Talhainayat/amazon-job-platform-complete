"""add pay currency"""
from alembic import op
import sqlalchemy as sa

revision = "h8i9j0k1l2m3"
down_revision = "g7h8i9j0k1l2"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("jobs", sa.Column("pay_currency", sa.String(length=3), nullable=False, server_default="CAD"))


def downgrade():
    op.drop_column("jobs", "pay_currency")