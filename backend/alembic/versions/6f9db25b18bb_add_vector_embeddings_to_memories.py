"""add vector embeddings to memories

Revision ID: 6f9db25b18bb
Revises: 78ea6e759ebe
Create Date: 2026-11-11 12:36:01.930051

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = '6f9db25b18bb'
down_revision: Union[str, Sequence[str], None] = '78ea6e759ebe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "memories",
        sa.Column(
            "embedding",
            Vector(384),
            nullable=True
        )
    )

def downgrade() -> None:
    op.drop_column("memories", "embedding")