"""Enhance memory_artifacts for job recovery, retry, and context notes.

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-11-17
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add context_notes column to memory_artifacts
    op.add_column(
        'memory_artifacts',
        sa.Column('context_notes', sa.Text(), nullable=True)
    )

    # 2. Add retry_count column to memory_artifacts
    op.add_column(
        'memory_artifacts',
        sa.Column('retry_count', sa.Integer(), server_default='0', nullable=False)
    )

    # 3. Add processing_started_at column for watchdog timeout detection
    op.add_column(
        'memory_artifacts',
        sa.Column('processing_started_at', sa.DateTime(timezone=True), nullable=True)
    )

    # 4. Composite index for per-user checksum idempotency
    op.create_index(
        'ix_memory_artifacts_user_checksum',
        'memory_artifacts',
        ['user_id', 'checksum_sha256'],
        unique=False
    )


def downgrade() -> None:
    op.drop_index('ix_memory_artifacts_user_checksum', table_name='memory_artifacts')
    op.drop_column('memory_artifacts', 'processing_started_at')
    op.drop_column('memory_artifacts', 'retry_count')
    op.drop_column('memory_artifacts', 'context_notes')
