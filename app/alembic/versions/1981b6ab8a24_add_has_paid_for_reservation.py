"""Add has_paid for reservation

Revision ID: 1981b6ab8a24
Revises: 60f0682fd70f
Create Date: 2024-10-19 18:47:40.980693

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '1981b6ab8a24'
down_revision = '60f0682fd70f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('reservationmodel', sa.Column('has_paid', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('reservationmodel', 'has_paid')
    # ### end Alembic commands ###
