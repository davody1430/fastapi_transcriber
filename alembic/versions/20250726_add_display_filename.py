"""add display_filename column to transcriptions

Revision ID: 4cbe5f921234
Revises: eddd757e9a71
Create Date: 2025-07-26 18:40:00
"""

from alembic import op
import sqlalchemy as sa

# شناسه‌های مهاجرت
revision = "4cbe5f921234"
down_revision = "eddd757e9a71"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    cols = [c["name"] for c in conn.execute("PRAGMA table_info('transcriptions')")]
    if "display_filename" not in cols:
        op.add_column(
            "transcriptions",
            sa.Column("display_filename", sa.String(), nullable=False, server_default="pending_file"),
        )
        op.execute(
            "UPDATE transcriptions SET display_filename = original_filename WHERE display_filename = 'pending_file'"
        )

def downgrade():
    # حذف ستون هنگام Rollback
    op.drop_column("transcriptions", "display_filename")
