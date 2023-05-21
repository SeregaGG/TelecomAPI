"""init revision

Revision ID: f9c8f754d7cf
Revises: 
Create Date: 2023-05-21 19:26:01.870475

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f9c8f754d7cf'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('equipment_type',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('type_name', sa.String(length=50), nullable=False),
    sa.Column('serial_mask', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('equipment',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('equipment_type_id', sa.Integer(), nullable=False),
    sa.Column('serial_number', sa.String(length=50), nullable=False),
    sa.Column('comment', sa.String(length=50), nullable=True),
    sa.ForeignKeyConstraint(['equipment_type_id'], ['equipment_type.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('equipment_type_id', 'serial_number')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('equipment')
    op.drop_table('equipment_type')
    # ### end Alembic commands ###