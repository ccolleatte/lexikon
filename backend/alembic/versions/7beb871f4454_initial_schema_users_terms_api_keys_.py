"""Initial schema: users, terms, api_keys, onboarding_sessions

Revision ID: 7beb871f4454
Revises: 
Create Date: 2025-11-20 22:57:50.914963

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7beb871f4454'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial schema with all tables."""

    # Create ENUM types (PostgreSQL-specific, will be ignored on SQLite)
    adoption_level_enum = sa.Enum('quick-project', 'research-project', 'production-api', name='adoptionlevelenum')
    term_level_enum = sa.Enum('quick-draft', 'ready', 'expert', name='termlevelenum')
    term_status_enum = sa.Enum('draft', 'ready', 'validated', name='termstatusenum')
    project_role_enum = sa.Enum('owner', 'editor', 'reviewer', 'viewer', name='projectroleenum')

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password_hash', sa.String(), nullable=True),
        sa.Column('first_name', sa.String(), nullable=False),
        sa.Column('last_name', sa.String(), nullable=False),
        sa.Column('institution', sa.String(), nullable=True),
        sa.Column('primary_domain', sa.String(), nullable=True),
        sa.Column('language', sa.String(), nullable=False),
        sa.Column('country', sa.String(length=2), nullable=True),
        sa.Column('adoption_level', adoption_level_enum, nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=False)

    # Create oauth_accounts table
    op.create_table(
        'oauth_accounts',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('provider', sa.String(), nullable=False),
        sa.Column('provider_user_id', sa.String(), nullable=False),
        sa.Column('access_token', sa.String(), nullable=True),
        sa.Column('refresh_token', sa.String(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create api_keys table
    op.create_table(
        'api_keys',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('key_hash', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('scopes', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key_hash')
    )
    op.create_index(op.f('ix_api_keys_key_hash'), 'api_keys', ['key_hash'], unique=False)

    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('language', sa.String(), nullable=False),
        sa.Column('primary_domain', sa.String(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=False),
        sa.Column('owner_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column('archived_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create project_members association table
    op.create_table(
        'project_members',
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('role', project_role_enum, nullable=False),
        sa.Column('joined_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('project_id', 'user_id')
    )

    # Create terms table
    op.create_table(
        'terms',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('definition', sa.Text(), nullable=False),
        sa.Column('domain', sa.String(), nullable=True),
        sa.Column('level', term_level_enum, nullable=False),
        sa.Column('status', term_status_enum, nullable=False),
        sa.Column('examples', sa.Text(), nullable=True),
        sa.Column('synonyms', sa.Text(), nullable=True),
        sa.Column('formal_definition', sa.Text(), nullable=True),
        sa.Column('citations', sa.Text(), nullable=True),
        sa.Column('term_metadata', sa.Text(), nullable=True),
        sa.Column('created_by', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_terms_name'), 'terms', ['name'], unique=False)

    # Create onboarding_sessions table
    op.create_table(
        'onboarding_sessions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('adoption_level', adoption_level_enum, nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create llm_configs table
    op.create_table(
        'llm_configs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('provider', sa.String(), nullable=False),
        sa.Column('api_key_encrypted', sa.String(), nullable=True),
        sa.Column('model_name', sa.String(), nullable=True),
        sa.Column('base_url', sa.String(), nullable=True),
        sa.Column('max_tokens', sa.Integer(), nullable=False),
        sa.Column('temperature', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )


def downgrade() -> None:
    """Drop all tables (reverse initial schema)."""
    op.drop_table('llm_configs')
    op.drop_table('onboarding_sessions')
    op.drop_table('terms')
    op.drop_table('project_members')
    op.drop_table('projects')
    op.drop_table('api_keys')
    op.drop_table('oauth_accounts')
    op.drop_table('users')
