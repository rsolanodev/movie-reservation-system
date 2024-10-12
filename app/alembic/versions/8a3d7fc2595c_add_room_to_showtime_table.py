"""Add Room to Showtime table

Revision ID: 8a3d7fc2595c
Revises: dab605a77cf4
Create Date: 2024-10-10 00:27:15.552412

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '8a3d7fc2595c'
down_revision = 'dab605a77cf4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('showtimemodel', sa.Column('room_id', sa.Uuid(), nullable=False))
    op.create_foreign_key(None, 'showtimemodel', 'roommodel', ['room_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'showtimemodel', type_='foreignkey')
    op.drop_column('showtimemodel', 'room_id')
    # ### end Alembic commands ###