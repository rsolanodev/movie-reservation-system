"""Remove has paid field

Revision ID: 569fcfafc8de
Revises: 4161ddbf2286
Create Date: 2025-01-06 13:14:30.803731

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '569fcfafc8de'
down_revision = '4161ddbf2286'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('reservationmodel', 'has_paid')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('reservationmodel', sa.Column('has_paid', sa.BOOLEAN(), autoincrement=False, nullable=False))
    # ### end Alembic commands ###
