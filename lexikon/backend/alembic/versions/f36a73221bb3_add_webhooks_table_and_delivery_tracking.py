"""Add webhooks table and delivery tracking

Revision ID: f36a73221bb3
Revises: b9d0965451a3
Create Date: 2025-11-21 02:17:02.703112

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f36a73221bb3'
down_revision: Union[str, Sequence[str], None] = 'b9d0965451a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add webhooks table and delivery tracking."""

    # Create webhooks table
    op.create_table(
        'webhooks',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('events', sa.String(), nullable=False),  # Comma-separated: "term_created,term_updated"
        sa.Column('secret', sa.String(), nullable=False),  # HMAC-SHA256 secret for signature
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('max_retries', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('retry_delay_seconds', sa.Integer(), nullable=False, server_default='60'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column('last_triggered_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('url', 'user_id')  # One URL per user
    )
    op.create_index(op.f('ix_webhooks_user_id'), 'webhooks', ['user_id'], unique=False)

    # Create webhook_deliveries table for tracking
    op.create_table(
        'webhook_deliveries',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('webhook_id', sa.String(), nullable=False),
        sa.Column('event_type', sa.String(), nullable=False),  # e.g., "term_created"
        sa.Column('payload', sa.Text(), nullable=False),  # JSON payload
        sa.Column('status', sa.String(), nullable=False),  # "pending", "success", "failed"
        sa.Column('response_status', sa.Integer(), nullable=True),  # HTTP status code
        sa.Column('response_body', sa.Text(), nullable=True),  # Response from webhook
        sa.Column('attempt_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_attempts', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('next_retry_at', sa.DateTime(), nullable=True),
        sa.Column('last_error', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column('delivered_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['webhook_id'], ['webhooks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_webhook_deliveries_webhook_id'), 'webhook_deliveries', ['webhook_id'], unique=False)
    op.create_index(op.f('ix_webhook_deliveries_status'), 'webhook_deliveries', ['status'], unique=False)
    op.create_index(op.f('ix_webhook_deliveries_next_retry_at'), 'webhook_deliveries', ['next_retry_at'], unique=False)


def downgrade() -> None:
    """Drop webhooks tables."""
    op.drop_index(op.f('ix_webhook_deliveries_next_retry_at'), table_name='webhook_deliveries')
    op.drop_index(op.f('ix_webhook_deliveries_status'), table_name='webhook_deliveries')
    op.drop_index(op.f('ix_webhook_deliveries_webhook_id'), table_name='webhook_deliveries')
    op.drop_table('webhook_deliveries')
    op.drop_index(op.f('ix_webhooks_user_id'), table_name='webhooks')
    op.drop_table('webhooks')
