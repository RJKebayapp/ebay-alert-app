"""create users table

Revision ID: manual_create_users
Revises: cfab9ed3e978
Create Date: 2025-03-26 20:XX:XX.XXXXXX

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'manual_create_users'
down_revision = 'cfab9ed3e978'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('email', sa.String(), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('subscription_tier', sa.String(), nullable=False, server_default='free')
    )

def downgrade():
    op.drop_table('users')
