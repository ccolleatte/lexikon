"""Initial schema

Revision ID: 0001
Revises:
Create Date: 2025-11-15 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password_hash', sa.String(), nullable=True),
        sa.Column('first_name', sa.String(), nullable=False),
        sa.Column('last_name', sa.String(), nullable=False),
        sa.Column('institution', sa.String(), nullable=True),
        sa.Column('primary_domain', sa.String(), nullable=True),
        sa.Column('language', sa.String(), nullable=False, server_default='fr'),
        sa.Column('country', sa.String(2), nullable=True),
        sa.Column('adoption_level', sa.String(), nullable=False, server_default='quick-project'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_users_email', 'users', ['email'], unique=True)

    # OAuth accounts table
    op.create_table(
        'oauth_accounts',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('provider', sa.String(), nullable=False),
        sa.Column('provider_user_id', sa.String(), nullable=False),
        sa.Column('access_token', sa.String(), nullable=True),
        sa.Column('refresh_token', sa.String(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # API keys table
    op.create_table(
        'api_keys',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('key_hash', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('scopes', sa.String(), nullable=False, server_default='read'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_api_keys_hash', 'api_keys', ['key_hash'], unique=True)

    # Projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('language', sa.String(), nullable=False, server_default='fr'),
        sa.Column('primary_domain', sa.String(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('owner_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('archived_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Project members association table
    op.create_table(
        'project_members',
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False, server_default='viewer'),
        sa.Column('joined_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('project_id', 'user_id')
    )

    # Terms table
    op.create_table(
        'terms',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('definition', sa.Text(), nullable=False),
        sa.Column('domain', sa.String(), nullable=True),
        sa.Column('level', sa.String(), nullable=False, server_default='quick-draft'),
        sa.Column('status', sa.String(), nullable=False, server_default='draft'),
        sa.Column('examples', sa.Text(), nullable=True),
        sa.Column('synonyms', sa.Text(), nullable=True),
        sa.Column('formal_definition', sa.Text(), nullable=True),
        sa.Column('citations', sa.Text(), nullable=True),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.Column('created_by', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_terms_name', 'terms', ['name'])
    op.create_index('idx_terms_project', 'terms', ['project_id'])

    # Onboarding sessions table
    op.create_table(
        'onboarding_sessions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('adoption_level', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # LLM configs table
    op.create_table(
        'llm_configs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('provider', sa.String(), nullable=False),
        sa.Column('api_key_encrypted', sa.String(), nullable=True),
        sa.Column('model_name', sa.String(), nullable=True),
        sa.Column('base_url', sa.String(), nullable=True),
        sa.Column('max_tokens', sa.Integer(), nullable=True, server_default='1000'),
        sa.Column('temperature', sa.Integer(), nullable=True, server_default='70'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )


def downgrade() -> None:
    op.drop_table('llm_configs')
    op.drop_table('onboarding_sessions')
    op.drop_index('idx_terms_project', table_name='terms')
    op.drop_index('idx_terms_name', table_name='terms')
    op.drop_table('terms')
    op.drop_table('project_members')
    op.drop_table('projects')
    op.drop_index('idx_api_keys_hash', table_name='api_keys')
    op.drop_table('api_keys')
    op.drop_table('oauth_accounts')
    op.drop_index('idx_users_email', table_name='users')
    op.drop_table('users')
