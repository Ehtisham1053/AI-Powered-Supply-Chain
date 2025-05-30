"""Add po_supplier table

Revision ID: 74724d1a2118
Revises: a90b9c0fc741
Create Date: 2025-05-13 21:28:57.756298

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '74724d1a2118'
down_revision = 'a90b9c0fc741'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('po_supplier',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('item', sa.Integer(), nullable=False),
    sa.Column('supplier_id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Float(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('processed_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('po_supplier')
    # ### end Alembic commands ###
