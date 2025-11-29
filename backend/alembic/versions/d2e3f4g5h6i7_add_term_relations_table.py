"""Add term_relations table for ontology reasoning

Revision ID: d2e3f4g5h6i7
Revises: c1d2e3f4g5h6
Create Date: 2025-11-26 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd2e3f4g5h6i7'
down_revision: Union[str, Sequence[str], None] = 'c1d2e3f4g5h6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create term_relations table for ontology reasoning."""
    op.create_table(
        'term_relations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('source_term_id', sa.String(), nullable=False),
        sa.Column('target_term_id', sa.String(), nullable=False),
        sa.Column('relation_type', sa.String(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('created_by', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['source_term_id'], ['terms.id'], ),
        sa.ForeignKeyConstraint(['target_term_id'], ['terms.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('source_term_id', 'target_term_id', 'relation_type', name='uq_term_relations')
    )

    # Create indexes for fast lookups
    op.create_index('ix_term_relations_source', 'term_relations', ['source_term_id'])
    op.create_index('ix_term_relations_target', 'term_relations', ['target_term_id'])
    op.create_index('ix_term_relations_type', 'term_relations', ['relation_type'])


def downgrade() -> None:
    """Remove term_relations table."""
    op.drop_index('ix_term_relations_type', table_name='term_relations')
    op.drop_index('ix_term_relations_target', table_name='term_relations')
    op.drop_index('ix_term_relations_source', table_name='term_relations')
    op.drop_table('term_relations')
