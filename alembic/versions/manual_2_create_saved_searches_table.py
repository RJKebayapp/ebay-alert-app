"""create saved_searches table

Revision ID: manual_2
Revises: c3cd5ca0ea68
Create Date: 2025-03-26 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'manual_2'
down_revision = 'c3cd5ca0ea68'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'saved_searches',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('search_query', sa.String(), nullable=False),
        sa.Column('min_price', sa.Integer(), nullable=True),
        sa.Column('max_price', sa.Integer(), nullable=True),
        sa.Column('frequency', sa.Integer(), nullable=False),
        sa.Column('locations', sa.String(), nullable=True),
        sa.Column('listing_type', sa.String(), nullable=False, server_default="Buy It Now New")
    )

def downgrade():
    op.drop_table('saved_searches')
