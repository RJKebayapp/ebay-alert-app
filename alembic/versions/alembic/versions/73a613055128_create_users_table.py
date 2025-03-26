
"""create users table"""

revision = '73a613055128'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(), unique=True, index=True, nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False)
    )


def downgrade():
    op.drop_table('users')
