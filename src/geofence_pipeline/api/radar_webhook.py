import hashlib
import hmac
import logging

from fastapi import FastAPI, Header, HTTPException, Request
from geofence_pipeline.config.settings import get_settings
from geofence_pipeline.domain.radar import normalize_radar_webhook
from geofence_pipeline.io.kinesis import KinesisProducer

logger = logging.getLogger(__name__)
app = FastAPI(title="Radar Webhook Receiver")


@app.post("/webhooks/radar")
async def radar_webhook(
    request: Request,
    x_radar_signature: str | None = Header(default=None),
    x_radar_signing_id: str | None = Header(default=None),
):
    settings = get_settings()
    if settings.radar_validate_signature and not _valid_signature(
        x_radar_signing_id,
        x_radar_signature,
        settings.radar_webhook_secret,
    ):
        raise HTTPException(status_code=401, detail="Invalid Radar signature")

    payload = await request.json()
    events = normalize_radar_webhook(payload)
    KinesisProducer(settings.radar_event_stream_name).put_geofence_events(events)
    logger.info("Published %s normalized Radar geofence events", len(events))
    return {"ok": True, "geofence_events": len(events)}


def _valid_signature(signing_id: str | None, signature: str | None, secret: str) -> bool:
    if not signing_id or not signature:
        return False
    digest = hmac.new(
        secret.encode("utf-8"),
        signing_id.encode("utf-8"),
        hashlib.sha1,
    ).hexdigest()
    expected_values = {digest, f"sha1={digest}"}
    return any(hmac.compare_digest(signature, expected) for expected in expected_values)
