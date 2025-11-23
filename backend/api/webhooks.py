"""
Webhook management API endpoints.
Provides endpoints for creating, managing, and testing webhooks.
"""

import secrets
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, HttpUrl, Field
from sqlalchemy.orm import Session
import uuid

from db.postgres import get_db, User, Webhook, WebhookDelivery
from auth.middleware import get_current_user
from events import EventType, WebhookDeliveryManager
from models import ApiResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


# Request/Response Models
class CreateWebhookRequest(BaseModel):
    """Request to create a webhook."""
    url: HttpUrl
    events: str = Field(..., description="Comma-separated event types (e.g., 'term_created,term_updated')")
    description: str = Field(default="", max_length=500)
    max_retries: int = Field(default=5, ge=1, le=10)
    retry_delay_seconds: int = Field(default=60, ge=10, le=3600)


class WebhookResponse(BaseModel):
    """Webhook response model."""
    id: str
    url: str
    events: str
    description: str
    is_active: bool
    secret: str = Field(description="Only shown on creation")
    max_retries: int
    retry_delay_seconds: int
    created_at: str
    last_triggered_at: str | None


class WebhookDeliveryResponse(BaseModel):
    """Webhook delivery response model."""
    id: str
    event_type: str
    status: str
    response_status: int | None
    attempt_count: int
    max_attempts: int
    created_at: str
    delivered_at: str | None


# Endpoints
@router.post("", status_code=201)
async def create_webhook(
    request: CreateWebhookRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new webhook.

    Events available:
    - term_created
    - term_updated
    - term_deleted
    - user_registered
    - project_created
    - project_member_added
    """
    try:
        # Validate events
        valid_events = {e.value for e in EventType}
        requested_events = {e.strip() for e in request.events.split(",")}

        invalid = requested_events - valid_events
        if invalid:
            return ApiResponse(
                success=False,
                error={
                    "code": "INVALID_EVENTS",
                    "message": f"Invalid event types: {', '.join(invalid)}",
                    "details": {"valid_events": list(valid_events)},
                },
            )

        # Check for duplicates
        existing = db.query(Webhook).filter(
            Webhook.user_id == current_user.id,
            Webhook.url == str(request.url),
        ).first()

        if existing:
            return ApiResponse(
                success=False,
                error={
                    "code": "WEBHOOK_EXISTS",
                    "message": "A webhook for this URL already exists",
                },
            )

        # Generate secret
        secret = secrets.token_urlsafe(32)

        # Create webhook
        webhook = Webhook(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            url=str(request.url),
            events=request.events,
            secret=secret,
            description=request.description,
            is_active=True,
            max_retries=request.max_retries,
            retry_delay_seconds=request.retry_delay_seconds,
        )

        db.add(webhook)
        db.commit()
        db.refresh(webhook)

        logger.info(f"Webhook created: {webhook.id} for user {current_user.id}")

        return ApiResponse(
            success=True,
            data={
                "id": webhook.id,
                "url": webhook.url,
                "events": webhook.events,
                "description": webhook.description,
                "is_active": webhook.is_active,
                "secret": secret,  # Only shown on creation!
                "max_retries": webhook.max_retries,
                "retry_delay_seconds": webhook.retry_delay_seconds,
                "created_at": webhook.created_at.isoformat(),
                "last_triggered_at": webhook.last_triggered_at.isoformat() if webhook.last_triggered_at else None,
            },
        )

    except Exception as e:
        logger.error(f"Error creating webhook: {e}")
        raise


@router.get("")
async def list_webhooks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all webhooks for current user."""
    webhooks = db.query(Webhook).filter(
        Webhook.user_id == current_user.id
    ).order_by(Webhook.created_at.desc()).all()

    return ApiResponse(
        success=True,
        data=[
            {
                "id": w.id,
                "url": w.url,
                "events": w.events,
                "description": w.description,
                "is_active": w.is_active,
                "max_retries": w.max_retries,
                "retry_delay_seconds": w.retry_delay_seconds,
                "created_at": w.created_at.isoformat(),
                "last_triggered_at": w.last_triggered_at.isoformat() if w.last_triggered_at else None,
            }
            for w in webhooks
        ],
        metadata={"total": len(webhooks)},
    )


@router.get("/{webhook_id}")
async def get_webhook(
    webhook_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific webhook."""
    webhook = db.query(Webhook).filter(
        Webhook.id == webhook_id,
        Webhook.user_id == current_user.id,
    ).first()

    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    return ApiResponse(
        success=True,
        data={
            "id": webhook.id,
            "url": webhook.url,
            "events": webhook.events,
            "description": webhook.description,
            "is_active": webhook.is_active,
            "max_retries": webhook.max_retries,
            "retry_delay_seconds": webhook.retry_delay_seconds,
            "created_at": webhook.created_at.isoformat(),
            "last_triggered_at": webhook.last_triggered_at.isoformat() if webhook.last_triggered_at else None,
        },
    )


@router.patch("/{webhook_id}")
async def update_webhook(
    webhook_id: str,
    request: CreateWebhookRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a webhook."""
    webhook = db.query(Webhook).filter(
        Webhook.id == webhook_id,
        Webhook.user_id == current_user.id,
    ).first()

    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    webhook.events = request.events
    webhook.description = request.description
    webhook.max_retries = request.max_retries
    webhook.retry_delay_seconds = request.retry_delay_seconds

    db.commit()
    db.refresh(webhook)

    return ApiResponse(
        success=True,
        data={
            "id": webhook.id,
            "url": webhook.url,
            "events": webhook.events,
            "description": webhook.description,
            "is_active": webhook.is_active,
            "created_at": webhook.created_at.isoformat(),
        },
    )


@router.delete("/{webhook_id}", status_code=204)
async def delete_webhook(
    webhook_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a webhook."""
    webhook = db.query(Webhook).filter(
        Webhook.id == webhook_id,
        Webhook.user_id == current_user.id,
    ).first()

    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    db.delete(webhook)
    db.commit()

    logger.info(f"Webhook deleted: {webhook_id}")

    return None


@router.post("/{webhook_id}/toggle")
async def toggle_webhook(
    webhook_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Toggle webhook active status."""
    webhook = db.query(Webhook).filter(
        Webhook.id == webhook_id,
        Webhook.user_id == current_user.id,
    ).first()

    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    webhook.is_active = not webhook.is_active
    db.commit()

    return ApiResponse(
        success=True,
        data={"is_active": webhook.is_active},
    )


@router.get("/{webhook_id}/deliveries")
async def get_webhook_deliveries(
    webhook_id: str,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get delivery history for webhook."""
    webhook = db.query(Webhook).filter(
        Webhook.id == webhook_id,
        Webhook.user_id == current_user.id,
    ).first()

    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    deliveries = db.query(WebhookDelivery).filter(
        WebhookDelivery.webhook_id == webhook_id
    ).order_by(WebhookDelivery.created_at.desc()).limit(limit).all()

    return ApiResponse(
        success=True,
        data=[
            {
                "id": d.id,
                "event_type": d.event_type,
                "status": d.status,
                "response_status": d.response_status,
                "attempt_count": d.attempt_count,
                "max_attempts": d.max_attempts,
                "created_at": d.created_at.isoformat(),
                "delivered_at": d.delivered_at.isoformat() if d.delivered_at else None,
            }
            for d in deliveries
        ],
        metadata={"total": len(deliveries)},
    )
