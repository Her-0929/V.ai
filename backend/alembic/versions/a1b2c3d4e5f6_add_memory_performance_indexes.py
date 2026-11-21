"""add memory performance indexes

Revision ID: a1b2c3d4e5f6
Revises: 6f9db25b18bb
Create Date: 2026-11-12 15:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '6f9db25b18bb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Composite index for primary retrieval query
    op.create_index(
        'ix_memories_user_active',
        'memories', ['user_id', 'is_active'],
        unique=False
    )
    # Composite index for type-filtered queries
    op.create_index(
        'ix_memories_user_type',
        'memories', ['user_id', 'memory_type'],
        unique=False
    )
    # Composite index for importance-ranked queries
    op.create_index(
        'ix_memories_user_importance',
        'memories', ['user_id', 'importance'],
        unique=False
    )
    # Index for recency queries
    op.create_index(
        'ix_memories_last_accessed',
        'memories', ['last_accessed_at'],
        unique=False
    )
    # HNSW vector index for fast approximate nearest neighbor search
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_memories_embedding_hnsw "
        "ON memories USING hnsw (embedding vector_cosine_ops) "
        "WITH (m = 16, ef_construction = 64)"
    )

def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_memories_embedding_hnsw")
    op.drop_index('ix_memories_last_accessed', table_name='memories')
    op.drop_index('ix_memories_user_importance', table_name='memories')
    op.drop_index('ix_memories_user_type', table_name='memories')
    op.drop_index('ix_memories_user_active', table_name='memories')
