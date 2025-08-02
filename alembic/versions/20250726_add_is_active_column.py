"""add is_active column to users

Revision ID: 5f2c9e1a4567
Revises: 4cbe5f921234
Create Date: 2025-07-26 19:50:00
"""

from alembic import op
import sqlalchemy as sa

revision = "5f2c9e1a4567"          # ← یکتا باشد
down_revision = "4cbe5f921234"     # ← آخرین head فعلی شما
branch_labels = None
depends_on = None


def upgrade():
    # اگر ستون از قبل نبود اضافه شود
    conn = op.get_bind()
    cols = [row[1] for row in conn.exec_driver_sql("PRAGMA table_info(users)")]
    if "is_active" not in cols:
        op.add_column(
            "users",
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        )


def downgrade():
    op.drop_column("users", "is_active")
