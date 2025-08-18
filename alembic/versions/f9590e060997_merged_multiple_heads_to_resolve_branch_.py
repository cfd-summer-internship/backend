"""Merged multiple heads to resolve branch conflict

Revision ID: f9590e060997
Revises: 8a163fff4b72, 8feaa7d41925
Create Date: 2025-08-18 13:31:21.498342

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f9590e060997'
down_revision: Union[str, None] = ('8a163fff4b72', '8feaa7d41925')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
