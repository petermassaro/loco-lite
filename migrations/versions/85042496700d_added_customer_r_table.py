"""Added customer r table

Revision ID: 85042496700d
Revises: 9f40523319b7
Create Date: 2018-06-19 20:34:56.258809

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '85042496700d'
down_revision = '9f40523319b7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('customer',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('stripe_id', sa.String(length=120), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('stripe_id')
    )
    op.create_index(op.f('ix_customer_email'), 'customer', ['email'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_customer_email'), table_name='customer')
    op.drop_table('customer')
    # ### end Alembic commands ###
