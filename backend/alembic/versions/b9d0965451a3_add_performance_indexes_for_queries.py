"""Add performance indexes for queries

Revision ID: b9d0965451a3
Revises: 7beb871f4454
Create Date: 2025-11-20 23:25:51.587278

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b9d0965451a3'
down_revision: Union[str, Sequence[str], None] = '7beb871f4454'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add performance indexes for frequently queried fields."""

    # Index on terms.created_by for filtering terms by user
    op.create_index(
        op.f('ix_terms_created_by'),
        'terms',
        ['created_by'],
        unique=False
    )

    # Composite index on (terms.name, terms.created_by) for uniqueness check
    op.create_index(
        op.f('ix_terms_name_created_by'),
        'terms',
        ['name', 'created_by'],
        unique=False
    )

    # Index on terms.project_id for project filtering
    op.create_index(
        op.f('ix_terms_project_id'),
        'terms',
        ['project_id'],
        unique=False
    )

    # Index on api_keys.user_id for user lookup
    op.create_index(
        op.f('ix_api_keys_user_id'),
        'api_keys',
        ['user_id'],
        unique=False
    )

    # Index on oauth_accounts.user_id for user lookup
    op.create_index(
        op.f('ix_oauth_accounts_user_id'),
        'oauth_accounts',
        ['user_id'],
        unique=False
    )

    # Index on oauth_accounts provider_user_id for OAuth lookups
    op.create_index(
        op.f('ix_oauth_accounts_provider_user_id'),
        'oauth_accounts',
        ['provider', 'provider_user_id'],
        unique=False
    )

    # Index on projects.owner_id for project filtering
    op.create_index(
        op.f('ix_projects_owner_id'),
        'projects',
        ['owner_id'],
        unique=False
    )


def downgrade() -> None:
    """Remove performance indexes."""
    op.drop_index(op.f('ix_projects_owner_id'), table_name='projects')
    op.drop_index(op.f('ix_oauth_accounts_provider_user_id'), table_name='oauth_accounts')
    op.drop_index(op.f('ix_oauth_accounts_user_id'), table_name='oauth_accounts')
    op.drop_index(op.f('ix_api_keys_user_id'), table_name='api_keys')
    op.drop_index(op.f('ix_terms_project_id'), table_name='terms')
    op.drop_index(op.f('ix_terms_name_created_by'), table_name='terms')
    op.drop_index(op.f('ix_terms_created_by'), table_name='terms')
