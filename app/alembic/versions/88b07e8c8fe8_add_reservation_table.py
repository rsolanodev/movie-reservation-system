"""Add Reservation table

Revision ID: 88b07e8c8fe8
Revises: ac456404261c
Create Date: 2024-10-12 20:59:35.646993

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '88b07e8c8fe8'
down_revision = 'ac456404261c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('reservationmodel',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('showtime_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['showtime_id'], ['showtimemodel.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['usermodel.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('seatmodel', sa.Column('reservation_id', sa.Uuid(), nullable=True))
    op.create_foreign_key(None, 'seatmodel', 'reservationmodel', ['reservation_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'seatmodel', type_='foreignkey')
    op.drop_column('seatmodel', 'reservation_id')
    op.drop_table('reservationmodel')
    # ### end Alembic commands ###
