"""add settings table, remove storage_quota from users

Revision ID: c3f7a1d09e44
Revises: bfe9eaa8fb22
Create Date: 2026-03-12 00:01:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c3f7a1d09e44'
down_revision = 'bfe9eaa8fb22'
branch_labels = None
depends_on = None

# Default quota constants (kept here so the seed data is self-contained)
DEFAULT_SUBSCRIBER_QUOTA = 10 * 1024 ** 3       # 10 GB
DEFAULT_LIMITED_SUBSCRIBER_QUOTA = 1 * 1024 ** 3  # 1 GB


def upgrade():
    # 1. Create settings table
    op.create_table(
        'settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('subscriber_quota', sa.BigInteger(), nullable=False,
                  server_default=str(DEFAULT_SUBSCRIBER_QUOTA)),
        sa.Column('limited_subscriber_quota', sa.BigInteger(), nullable=False,
                  server_default=str(DEFAULT_LIMITED_SUBSCRIBER_QUOTA)),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    # 2. Seed the singleton settings row
    op.execute(
        f"INSERT INTO settings (subscriber_quota, limited_subscriber_quota, updated_at) "
        f"VALUES ({DEFAULT_SUBSCRIBER_QUOTA}, {DEFAULT_LIMITED_SUBSCRIBER_QUOTA}, NOW())"
    )

    # 3. Remove storage_quota column from users
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('storage_quota')


def downgrade():
    # Re-add storage_quota with the old 5 GB default
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('storage_quota', sa.BigInteger(),
                      nullable=True, server_default='5368709120')
        )

    # Drop the settings table
    op.drop_table('settings')
