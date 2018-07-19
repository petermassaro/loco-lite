"""ChChanged employee table to user table

Revision ID: 442d9903ab11
Revises: 85042496700d
Create Date: 2018-07-01 16:29:39.181141

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '442d9903ab11'
down_revision = '85042496700d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('access_level', sa.String(length=120), nullable=True),
    sa.Column('phone', sa.String(length=20), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('phone')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.drop_index('ix_employee_email', table_name='employee')
    op.drop_table('employee')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('employee',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('email', sa.VARCHAR(length=120), nullable=True),
    sa.Column('password_hash', sa.VARCHAR(length=128), nullable=True),
    sa.Column('access_level', sa.VARCHAR(length=120), nullable=True),
    sa.Column('phone', sa.VARCHAR(length=20), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('phone')
    )
    op.create_index('ix_employee_email', 'employee', ['email'], unique=1)
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    # ### end Alembic commands ###