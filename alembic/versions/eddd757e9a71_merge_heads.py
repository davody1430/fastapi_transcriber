"""merge heads

Revision ID: eddd757e9a71
Revises: 2b9a7b112345, a325d151ad71
Create Date: 2025-07-26 12:27:09.057389

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eddd757e9a71'
down_revision: Union[str, Sequence[str], None] = ('2b9a7b112345', 'a325d151ad71')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
