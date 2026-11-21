"""add memory artifacts and temporal columns

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-11-13 14:15:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, Sequence[str], None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create memory_artifacts table
    op.create_table(
        'memory_artifacts',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('artifact_type', sa.String(length=30), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('storage_path', sa.String(length=500), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=False),
        sa.Column('file_size_bytes', sa.BigInteger(), nullable=False),
        sa.Column('checksum_sha256', sa.String(length=64), nullable=False),
        sa.Column('status', sa.String(length=30), server_default='pending', nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "artifact_type IN ('note', 'letter', 'document', 'photo', 'audio_transcript')",
            name='ck_artifact_type'
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'processing', 'completed', 'failed')",
            name='ck_artifact_status'
        ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_memory_artifacts_user_id'), 'memory_artifacts', ['user_id'], unique=False)
    op.create_index(op.f('ix_memory_artifacts_artifact_type'), 'memory_artifacts', ['artifact_type'], unique=False)
    op.create_index(op.f('ix_memory_artifacts_status'), 'memory_artifacts', ['status'], unique=False)
    op.create_index(op.f('ix_memory_artifacts_checksum_sha256'), 'memory_artifacts', ['checksum_sha256'], unique=False)
    op.create_index(op.f('ix_memory_artifacts_created_at'), 'memory_artifacts', ['created_at'], unique=False)
    op.create_index('ix_memory_artifacts_user_id_status', 'memory_artifacts', ['user_id', 'status'], unique=False)

    # 2. Add temporal and status columns to memories table
    op.add_column('memories', sa.Column('event_date', sa.Date(), nullable=True))
    op.add_column('memories', sa.Column('event_date_precision', sa.String(length=20), server_default='unknown', nullable=False))
    op.add_column('memories', sa.Column('source_created_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('memories', sa.Column('status', sa.String(length=30), server_default='active', nullable=False))
    op.add_column('memories', sa.Column('superseded_by_id', sa.Uuid(), nullable=True))
    op.add_column('memories', sa.Column('access_scope', sa.String(length=30), server_default='default', nullable=False))
    op.add_column('memories', sa.Column('version', sa.Integer(), server_default='1', nullable=False))

    op.create_check_constraint(
        'ck_memory_event_date_precision',
        'memories',
        "event_date_precision IN ('day', 'month', 'year', 'decade', 'unknown')"
    )
    op.create_check_constraint(
        'ck_memory_status',
        'memories',
        "status IN ('active', 'superseded', 'disputed')"
    )
    op.create_check_constraint(
        'ck_memory_access_scope',
        'memories',
        "access_scope IN ('default', 'private', 'archival')"
    )
    op.create_check_constraint(
        'ck_memory_no_self_supersede',
        'memories',
        "superseded_by_id IS NULL OR superseded_by_id != id"
    )

    op.create_foreign_key(
        'fk_memories_superseded_by_id',
        'memories',
        'memories',
        ['superseded_by_id'],
        ['id'],
        ondelete='SET NULL'
    )
    op.create_index(op.f('ix_memories_event_date'), 'memories', ['event_date'], unique=False)
    op.create_index(op.f('ix_memories_status'), 'memories', ['status'], unique=False)
    op.create_index(op.f('ix_memories_superseded_by_id'), 'memories', ['superseded_by_id'], unique=False)

    # 3. Add artifact reference and metadata to memory_sources table
    op.add_column('memory_sources', sa.Column('artifact_id', sa.Uuid(), nullable=True))
    op.add_column('memory_sources', sa.Column('source_location', sa.String(length=255), nullable=True))
    op.add_column('memory_sources', sa.Column('source_metadata', sa.JSON(), nullable=True))

    op.create_foreign_key(
        'fk_memory_sources_artifact_id',
        'memory_sources',
        'memory_artifacts',
        ['artifact_id'],
        ['id'],
        ondelete='CASCADE'
    )
    op.create_index(op.f('ix_memory_sources_artifact_id'), 'memory_sources', ['artifact_id'], unique=False)

    # Update source_type constraint on memory_sources
    op.drop_constraint('ck_memory_source_type', 'memory_sources', type_='check')
    op.create_check_constraint(
        'ck_memory_source_type',
        'memory_sources',
        "source_type IN ('message', 'letter', 'note', 'document', 'photo', 'audio', 'manual', 'imported', 'system')"
    )


def downgrade() -> None:
    # 3. Revert memory_sources changes
    op.drop_constraint('ck_memory_source_type', 'memory_sources', type_='check')
    op.create_check_constraint(
        'ck_memory_source_type',
        'memory_sources',
        "source_type IN ('message', 'manual', 'imported', 'system')"
    )
    op.drop_index(op.f('ix_memory_sources_artifact_id'), table_name='memory_sources')
    op.drop_constraint('fk_memory_sources_artifact_id', 'memory_sources', type_='foreignkey')
    op.drop_column('memory_sources', 'source_metadata')
    op.drop_column('memory_sources', 'source_location')
    op.drop_column('memory_sources', 'artifact_id')

    # 2. Revert memories changes
    op.drop_index(op.f('ix_memories_superseded_by_id'), table_name='memories')
    op.drop_index(op.f('ix_memories_status'), table_name='memories')
    op.drop_index(op.f('ix_memories_event_date'), table_name='memories')
    op.drop_constraint('fk_memories_superseded_by_id', 'memories', type_='foreignkey')
    op.drop_constraint('ck_memory_no_self_supersede', 'memories', type_='check')
    op.drop_constraint('ck_memory_access_scope', 'memories', type_='check')
    op.drop_constraint('ck_memory_status', 'memories', type_='check')
    op.drop_constraint('ck_memory_event_date_precision', 'memories', type_='check')
    op.drop_column('memories', 'version')
    op.drop_column('memories', 'access_scope')
    op.drop_column('memories', 'superseded_by_id')
    op.drop_column('memories', 'status')
    op.drop_column('memories', 'source_created_at')
    op.drop_column('memories', 'event_date_precision')
    op.drop_column('memories', 'event_date')

    # 1. Drop memory_artifacts table
    op.drop_index('ix_memory_artifacts_user_id_status', table_name='memory_artifacts')
    op.drop_index(op.f('ix_memory_artifacts_created_at'), table_name='memory_artifacts')
    op.drop_index(op.f('ix_memory_artifacts_checksum_sha256'), table_name='memory_artifacts')
    op.drop_index(op.f('ix_memory_artifacts_status'), table_name='memory_artifacts')
    op.drop_index(op.f('ix_memory_artifacts_artifact_type'), table_name='memory_artifacts')
    op.drop_index(op.f('ix_memory_artifacts_user_id'), table_name='memory_artifacts')
    op.drop_table('memory_artifacts')

