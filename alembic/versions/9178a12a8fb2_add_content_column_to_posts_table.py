"""add content column to posts table

Revision ID: 9178a12a8fb2
Revises: b0d91163239c
Create Date: 2022-08-01 08:47:44.999997

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9178a12a8fb2'
down_revision = 'b0d91163239c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'posts',
        sa.Column('content', sa.String(), nullable=False)
        )
    pass


def downgrade() -> None:
    op.drop_column('posts', 'content')
    pass
