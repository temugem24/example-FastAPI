"""testing

Revision ID: 294e234eaaa2
Revises: 
Create Date: 2024-06-03 20:59:37.493812

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '294e234eaaa2'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'posts',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('title', sa.String(255), nullable=False)
    )   

def downgrade():
    op.drop_table('posts')
