"""add admin_quota to settings

Revision ID: d2e8b3f01c55
Revises: c3f7a1d09e44
Create Date: 2026-03-12 00:02:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'd2e8b3f01c55'
down_revision = 'c3f7a1d09e44'
branch_labels = None
depends_on = None

DEFAULT_ADMIN_QUOTA = 50 * 1024 ** 3  # 50 GB


def upgrade():
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('admin_quota', sa.BigInteger(), nullable=False,
                      server_default=str(DEFAULT_ADMIN_QUOTA))
        )

    # Populate the existing row in case server_default wasn't applied
    op.execute(f"UPDATE settings SET admin_quota = {DEFAULT_ADMIN_QUOTA}")


def downgrade():
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.drop_column('admin_quota')
