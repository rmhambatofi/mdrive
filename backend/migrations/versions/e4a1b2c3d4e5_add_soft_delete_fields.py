"""Add soft delete fields to files table

Revision ID: e4a1b2c3d4e5
Revises: d2e8b3f01c55
Create Date: 2026-03-12 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'e4a1b2c3d4e5'
down_revision = 'd2e8b3f01c55'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('files', sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('0')))
    op.add_column('files', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    op.add_column('files', sa.Column('original_parent_folder_uuid', sa.String(length=36), nullable=True))
    op.create_index('idx_user_deleted', 'files', ['user_uuid', 'is_deleted'])


def downgrade():
    op.drop_index('idx_user_deleted', table_name='files')
    op.drop_column('files', 'original_parent_folder_uuid')
    op.drop_column('files', 'deleted_at')
    op.drop_column('files', 'is_deleted')
