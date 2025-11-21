# Webhooks Guide

**Last Updated:** 2025-11-20
**Version:** 1.0

## Overview

Webhooks allow you to build or set up integrations which subscribe to certain events in Lexikon. When events occur, we send a POST request with event data to your webhook URL.

## Event Types

| Event | Trigger | Payload |
|-------|---------|---------|
| `term_created` | New term created | `term_id`, `term_name`, `domain`, `level`, `status` |
| `term_updated` | Term modified | `term_id`, `changes`: {old, new} |
| `term_deleted` | Term removed | `term_id`, `term_name` |
| `user_registered` | New user signup | `user_id`, `email`, `first_name`, `last_name` |
| `project_created` | New project created | `project_id`, `name`, `language` |
| `project_member_added` | Member joined project | `project_id`, `user_id`, `role` |

## Creating a Webhook

**POST** `/api/webhooks`

```json
{
  "url": "https://example.com/webhooks/lexikon",
  "events": "term_created,term_updated",
  "description": "My webhook integration",
  "max_retries": 5,
  "retry_delay_seconds": 60
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "url": "https://example.com/webhooks/lexikon",
    "events": "term_created,term_updated",
    "description": "My webhook integration",
    "is_active": true,
    "secret": "wh_super_secret_key_keep_safe",
    "max_retries": 5,
    "retry_delay_seconds": 60,
    "created_at": "2025-11-20T12:00:00Z",
    "last_triggered_at": null
  }
}
```

⚠️ **IMPORTANT**: The `secret` is only shown once on creation. Store it securely!

## Webhook Payload

Every webhook delivery includes headers and a JSON payload:

```json
{
  "id": "evt_abc123",
  "type": "term_created",
  "timestamp": "2025-11-20T12:00:00Z",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "data": {
    "term_id": "term_123",
    "term_name": "Machine Learning",
    "domain": "informatique",
    "level": "quick-draft",
    "status": "draft"
  }
}
```

### Headers

```
Content-Type: application/json
X-Lexikon-Event: term_created
X-Lexikon-Signature: sha256=hmac_sha256_hex_digest
X-Lexikon-Timestamp: 2025-11-20T12:00:00Z
```

## Signature Validation

Verify webhook authenticity using HMAC-SHA256:

### Python
```python
import hmac
import hashlib
import json

def verify_signature(payload_json: str, signature: str, secret: str) -> bool:
    """Verify webhook signature."""
    expected = hmac.new(
        secret.encode('utf-8'),
        payload_json.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected, signature)

# Webhook handler
@app.post('/webhooks/lexikon')
async def handle_webhook(request: Request):
    payload = await request.json()
    signature = request.headers.get('X-Lexikon-Signature').replace('sha256=', '')

    if not verify_signature(json.dumps(payload), signature, SECRET):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Process event
    handle_event(payload['type'], payload['data'])
```

### Node.js
```javascript
const crypto = require('crypto');

function verifySignature(payload, signature, secret) {
  const expected = crypto
    .createHmac('sha256', secret)
    .update(payload)
    .digest('hex');

  return crypto.timingSafeEqual(expected, signature);
}

// Webhook handler
app.post('/webhooks/lexikon', (req, res) => {
  const signature = req.headers['x-lexikon-signature'].replace('sha256=', '');
  const payload = JSON.stringify(req.body);

  if (!verifySignature(payload, signature, WEBHOOK_SECRET)) {
    return res.status(401).json({ error: 'Invalid signature' });
  }

  // Process event
  handleEvent(req.body.type, req.body.data);
  res.json({ ok: true });
});
```

## Retry Logic

Failed deliveries are retried with exponential backoff:

| Attempt | Delay | Cumulative |
|---------|-------|-----------|
| 1 | immediate | 0s |
| 2 | 60s | 60s |
| 3 | 120s | 180s |
| 4 | 240s | 420s |
| 5 | 480s | 900s (~15 min) |

After 5 failures, the delivery is marked as permanently failed.

## API Endpoints

### List Webhooks
**GET** `/api/webhooks`

```json
{
  "success": true,
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "url": "https://example.com/webhooks/lexikon",
      "events": "term_created,term_updated",
      "is_active": true,
      "created_at": "2025-11-20T12:00:00Z"
    }
  ],
  "metadata": { "total": 1 }
}
```

### Get Webhook
**GET** `/api/webhooks/{webhook_id}`

### Update Webhook
**PATCH** `/api/webhooks/{webhook_id}`

```json
{
  "events": "term_created,term_updated,term_deleted",
  "description": "Updated description"
}
```

### Delete Webhook
**DELETE** `/api/webhooks/{webhook_id}`

### Toggle Webhook
**POST** `/api/webhooks/{webhook_id}/toggle`

Returns: `{ "success": true, "data": { "is_active": false } }`

### Get Deliveries
**GET** `/api/webhooks/{webhook_id}/deliveries?limit=50`

```json
{
  "success": true,
  "data": [
    {
      "id": "dlv_123",
      "event_type": "term_created",
      "status": "success",
      "response_status": 200,
      "attempt_count": 1,
      "created_at": "2025-11-20T12:00:00Z",
      "delivered_at": "2025-11-20T12:00:01Z"
    }
  ]
}
```

## Best Practices

### 1. Validate Signatures
Always verify the webhook signature before processing:
- Prevents replay attacks
- Ensures authenticity
- Protects against tampering

### 2. Return Quickly
Webhook handlers should return 2xx status immediately:
```python
@app.post('/webhooks/lexikon')
async def handle_webhook(request: Request):
    # Validate signature
    # Queue event for processing
    return { "ok": true }  # Return immediately

    # Background: Process event asynchronously
    asyncio.create_task(process_event(event))
```

### 3. Idempotent Processing
Handle duplicate deliveries gracefully:
```python
# Use event ID to detect duplicates
event_id = payload['id']
if already_processed(event_id):
    return { "ok": true }  # Already processed, return success
```

### 4. Log Events
Track all webhook activity:
```python
logger.info(f"Webhook received: {payload['type']} from {request.client.host}")
```

### 5. Handle Errors Gracefully
Return proper HTTP status codes:
- `2xx`: Success (delivery complete)
- `4xx`: Client error (don't retry)
- `5xx`: Server error (will retry)

## Implementation Example

### Complete Python Handler

```python
from fastapi import FastAPI, Request, HTTPException
import hmac
import hashlib
import json
import asyncio

app = FastAPI()
WEBHOOK_SECRET = "wh_your_secret_key"

def verify_signature(payload: str, signature: str) -> bool:
    """Verify HMAC-SHA256 signature."""
    expected = hmac.new(
        WEBHOOK_SECRET.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)

async def process_event(event_type: str, data: dict):
    """Process webhook event asynchronously."""
    if event_type == 'term_created':
        print(f"New term: {data['term_name']}")
    elif event_type == 'term_updated':
        print(f"Updated term: {data['term_id']}")
    # ... handle other events

@app.post('/webhooks/lexikon')
async def handle_webhook(request: Request):
    try:
        # Get signature from headers
        signature = request.headers.get('X-Lexikon-Signature', '').replace('sha256=', '')

        # Read body
        payload = await request.body()
        payload_str = payload.decode('utf-8')

        # Verify signature
        if not verify_signature(payload_str, signature):
            raise HTTPException(status_code=401, detail="Invalid signature")

        # Parse JSON
        event = json.loads(payload_str)

        # Process asynchronously
        asyncio.create_task(process_event(event['type'], event['data']))

        # Return immediately
        return { "ok": True }

    except Exception as e:
        print(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal error")
```

## Troubleshooting

### "Invalid signature" errors
- Verify the secret is correct
- Ensure signature validation uses exact payload JSON
- Check header parsing: format is `sha256=hexdigest`

### Delivery not reaching endpoint
- Check webhook URL is accessible from Lexikon servers
- Verify firewall rules allow inbound requests
- Check DNS resolution
- Review webhook delivery logs

### Retry storm
- Endpoint not returning 2xx status
- Fix endpoint and webhook will retry automatically
- Review "Get Deliveries" endpoint for status

## Related Files

- **System**: `events/webhook_system.py`
- **API**: `api/webhooks.py`
- **Models**: `db/postgres.py` (Webhook, WebhookDelivery)
- **Migration**: `alembic/versions/f36a73221bb3_*`

## Further Reading

- [HMAC-SHA256 Verification](https://tools.ietf.org/html/rfc2104)
- [Webhook Best Practices](https://docs.github.com/en/developers/webhooks-and-events/webhooks/best-practices-for-webhooks)
- [Event Delivery Patterns](https://en.wikipedia.org/wiki/Webhook)
