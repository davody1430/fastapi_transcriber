"""add celery_task_id column

Revision ID: 2b9a7b112345
Revises: 1d752a821f3a
Create Date: 2025-07-26 12:25:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "2b9a7b112345"
down_revision = "1d752a821f3a"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "transcriptions",
        sa.Column("celery_task_id", sa.String(length=50), nullable=True, index=True),
    )


def downgrade():
    op.drop_column("transcriptions", "celery_task_id")
