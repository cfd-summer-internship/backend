"""removed unique constraint from survey questions

Revision ID: dfebb09fd71a
Revises: cfde1e95dec6
Create Date: 2025-07-14 14:59:38.201627

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = 'dfebb09fd71a'
down_revision: Union[str, None] = 'cfde1e95dec6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)
    constraints = [c['name'] for c in inspector.get_unique_constraints("survey_question")]
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    if "survey_question_survey_config_id_key" in constraints:
        op.drop_constraint(op.f('survey_question_survey_config_id_key'), 'survey_question', type_='unique')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(op.f('survey_question_survey_config_id_key'), 'survey_question', ['survey_config_id'], postgresql_nulls_not_distinct=False)
    # ### end Alembic commands ###
