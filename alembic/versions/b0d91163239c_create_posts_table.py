"""create posts table

Revision ID: b0d91163239c
Revises: 
Create Date: 2022-08-01 08:30:42.692524

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b0d91163239c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'posts', 
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('title', sa.String(), nullable=False)
        )
    pass


def downgrade() -> None:
    op.drop_table('posts')
    pass
