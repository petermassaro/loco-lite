"""Added role column to user table

Revision ID: 138629a4cb14
Revises: 442d9903ab11
Create Date: 2018-07-01 21:07:40.362635

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '138629a4cb14'
down_revision = '442d9903ab11'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('role', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'role')
    # ### end Alembic commands ###