"""
Webhook event system with delivery and retry logic.
Handles event publishing, webhook delivery, and retry management.
"""

import json
import hmac
import hashlib
import logging
import httpx
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from enum import Enum
from uuid import uuid4

from sqlalchemy.orm import Session
from sqlalchemy import and_

logger = logging.getLogger(__name__)

# Event types
class EventType(Enum):
    """Webhook event types."""
    TERM_CREATED = "term_created"
    TERM_UPDATED = "term_updated"
    TERM_DELETED = "term_deleted"
    USER_REGISTERED = "user_registered"
    PROJECT_CREATED = "project_created"
    PROJECT_MEMBER_ADDED = "project_member_added"


class WebhookEvent:
    """Webhook event data."""

    def __init__(
        self,
        event_type: EventType,
        user_id: str,
        data: Dict[str, Any],
        timestamp: Optional[datetime] = None,
    ):
        self.id = str(uuid4())
        self.event_type = event_type.value
        self.user_id = user_id
        self.data = data
        self.timestamp = timestamp or datetime.utcnow()

    def to_payload(self) -> Dict[str, Any]:
        """Serialize event to JSON payload."""
        return {
            "id": self.id,
            "type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "data": self.data,
        }


class WebhookSignature:
    """HMAC-SHA256 signature generation and validation."""

    @staticmethod
    def generate(secret: str, payload_json: str) -> str:
        """
        Generate HMAC-SHA256 signature for payload.

        Args:
            secret: Webhook secret key
            payload_json: JSON string of payload

        Returns:
            Hex-encoded HMAC signature
        """
        signature = hmac.new(
            secret.encode("utf-8"),
            payload_json.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return signature

    @staticmethod
    def validate(secret: str, payload_json: str, signature: str) -> bool:
        """
        Validate HMAC-SHA256 signature.

        Args:
            secret: Webhook secret key
            payload_json: JSON string of payload
            signature: Signature to validate

        Returns:
            True if signature is valid
        """
        expected = WebhookSignature.generate(secret, payload_json)
        # Use constant-time comparison to prevent timing attacks
        return hmac.compare_digest(expected, signature)


class WebhookDeliveryManager:
    """Manages webhook delivery and retries."""

    # Constants
    DEFAULT_TIMEOUT = 10  # seconds
    MAX_PAYLOAD_SIZE = 1_000_000  # 1MB
    RETRY_BACKOFF_BASE = 2  # Exponential backoff: 60s, 120s, 240s...

    def __init__(self, db: Session):
        self.db = db

    def deliver_event(self, event: WebhookEvent) -> int:
        """
        Deliver event to all active webhooks for user.

        Args:
            event: WebhookEvent to deliver

        Returns:
            Number of webhook deliveries created
        """
        from db.postgres import Webhook, WebhookDelivery

        # Find active webhooks for this user that handle this event
        webhooks = self.db.query(Webhook).filter(
            and_(
                Webhook.user_id == event.user_id,
                Webhook.is_active == True,
            )
        ).all()

        delivery_count = 0
        payload_json = json.dumps(event.to_payload())

        for webhook in webhooks:
            if not webhook.should_handle_event(event.event_type):
                continue

            # Create delivery record
            signature = WebhookSignature.generate(webhook.secret, payload_json)

            delivery = WebhookDelivery(
                id=str(uuid4()),
                webhook_id=webhook.id,
                event_type=event.event_type,
                payload=payload_json,
                status="pending",
                attempt_count=0,
                max_attempts=webhook.max_retries,
                next_retry_at=datetime.utcnow(),  # Try immediately
            )

            self.db.add(delivery)
            delivery_count += 1

            # Try delivery
            self._attempt_delivery(delivery, webhook, payload_json, signature)

        if delivery_count > 0:
            self.db.commit()

        logger.info(
            f"Created {delivery_count} webhook deliveries for event {event.event_type}"
        )

        return delivery_count

    def _attempt_delivery(
        self,
        delivery: "WebhookDelivery",
        webhook: "Webhook",
        payload_json: str,
        signature: str,
    ) -> bool:
        """
        Attempt to deliver webhook.

        Returns:
            True if successful
        """
        if delivery.next_retry_at and delivery.next_retry_at > datetime.utcnow():
            logger.debug(f"Webhook {webhook.id} not yet ready for retry")
            return False

        try:
            delivery.attempt_count += 1

            # Prepare headers with signature
            headers = {
                "Content-Type": "application/json",
                "X-Lexikon-Event": delivery.event_type,
                "X-Lexikon-Signature": f"sha256={signature}",
                "X-Lexikon-Timestamp": datetime.utcnow().isoformat(),
            }

            # Send webhook
            with httpx.Client(timeout=self.DEFAULT_TIMEOUT) as client:
                response = client.post(webhook.url, content=payload_json, headers=headers)

                delivery.response_status = response.status_code
                delivery.response_body = response.text[:1000]  # Store first 1KB

                if 200 <= response.status_code < 300:
                    # Success
                    delivery.status = "success"
                    delivery.delivered_at = datetime.utcnow()
                    webhook.last_triggered_at = datetime.utcnow()

                    logger.info(
                        f"✅ Webhook {webhook.id} delivered successfully "
                        f"(attempt {delivery.attempt_count})"
                    )

                    self.db.commit()
                    return True
                else:
                    # Server error - retry
                    logger.warning(
                        f"⚠️ Webhook {webhook.id} returned {response.status_code} "
                        f"(attempt {delivery.attempt_count}/{delivery.max_attempts})"
                    )

                    self._schedule_retry(delivery, webhook)
                    self.db.commit()
                    return False

        except httpx.TimeoutException:
            delivery.last_error = "Request timeout"
            self._schedule_retry(delivery, webhook)
            logger.warning(f"⏱️ Webhook {webhook.id} timeout (attempt {delivery.attempt_count})")
            self.db.commit()
            return False

        except Exception as e:
            delivery.last_error = str(e)
            self._schedule_retry(delivery, webhook)
            logger.error(f"❌ Webhook {webhook.id} error: {e}")
            self.db.commit()
            return False

    def _schedule_retry(self, delivery: "WebhookDelivery", webhook: "Webhook"):
        """Schedule next retry with exponential backoff."""
        if delivery.attempt_count >= delivery.max_attempts:
            delivery.status = "failed"
            logger.error(
                f"❌ Webhook {webhook.id} permanently failed after {delivery.max_attempts} attempts"
            )
            return

        # Exponential backoff: 60s, 120s, 240s, 480s, etc.
        delay_seconds = webhook.retry_delay_seconds * (
            self.RETRY_BACKOFF_BASE ** (delivery.attempt_count - 1)
        )
        delivery.next_retry_at = datetime.utcnow() + timedelta(seconds=delay_seconds)
        delivery.status = "pending"

        logger.info(
            f"⏳ Webhook {webhook.id} retry scheduled in {delay_seconds}s "
            f"(attempt {delivery.attempt_count + 1}/{delivery.max_attempts})"
        )

    def retry_pending_deliveries(self):
        """Retry pending webhook deliveries that are ready."""
        from db.postgres import WebhookDelivery, Webhook

        now = datetime.utcnow()

        # Find ready deliveries
        pending = self.db.query(WebhookDelivery).filter(
            and_(
                WebhookDelivery.status == "pending",
                WebhookDelivery.next_retry_at <= now,
            )
        ).all()

        logger.debug(f"Found {len(pending)} webhooks ready for retry")

        for delivery in pending:
            webhook = delivery.webhook

            if not webhook.is_active:
                delivery.status = "failed"
                continue

            payload_json = delivery.payload
            signature = WebhookSignature.generate(webhook.secret, payload_json)

            self._attempt_delivery(delivery, webhook, payload_json, signature)

    def get_delivery_history(
        self, webhook_id: str, limit: int = 50
    ) -> List["WebhookDelivery"]:
        """Get delivery history for webhook."""
        from db.postgres import WebhookDelivery

        return self.db.query(WebhookDelivery).filter(
            WebhookDelivery.webhook_id == webhook_id
        ).order_by(WebhookDelivery.created_at.desc()).limit(limit).all()


# Global webhook manager (lazy initialization)
_delivery_manager: Optional[WebhookDeliveryManager] = None


def get_webhook_delivery_manager(db: Session) -> WebhookDeliveryManager:
    """Get webhook delivery manager."""
    return WebhookDeliveryManager(db)


async def publish_event(db: Session, event: WebhookEvent):
    """
    Publish event and deliver to webhooks.

    Usage:
        event = WebhookEvent(
            event_type=EventType.TERM_CREATED,
            user_id=current_user.id,
            data={
                "term_id": term.id,
                "term_name": term.name,
                "domain": term.domain,
            }
        )
        await publish_event(db, event)
    """
    manager = WebhookDeliveryManager(db)
    manager.deliver_event(event)
