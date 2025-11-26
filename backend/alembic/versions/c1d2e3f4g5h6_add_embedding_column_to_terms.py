"""Add embedding column to terms for semantic search

Revision ID: c1d2e3f4g5h6
Revises: f36a73221bb3
Create Date: 2025-11-26 11:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1d2e3f4g5h6'
down_revision: Union[str, Sequence[str], None] = 'f36a73221bb3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add embedding column to terms table for semantic search."""
    # Note: pgvector type will be handled automatically by SQLAlchemy if using PostgreSQL
    # For SQLite, this is stored as JSON/TEXT (not ideal but functional for development)
    op.add_column('terms',
        sa.Column('embedding', sa.Text(), nullable=True,
            comment='Vector embedding for semantic search (JSON serialized list of floats)')
    )

    # Add index for faster similarity searches (PostgreSQL only)
    # SQLite will ignore this, which is fine for development
    try:
        op.execute('CREATE INDEX idx_terms_embedding ON terms USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)')
    except:
        # Silently fail if pgvector not available (e.g., SQLite)
        pass


def downgrade() -> None:
    """Remove embedding column from terms table."""
    op.drop_index('idx_terms_embedding', table_name='terms', if_exists=True)
    op.drop_column('terms', 'embedding')
