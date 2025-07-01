"""moved survey

Revision ID: 90f6e05b7bcd
Revises: 4d1abec2a9fe
Create Date: 2025-06-30 20:29:15.559578

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '90f6e05b7bcd'
down_revision: Union[str, None] = '4d1abec2a9fe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
