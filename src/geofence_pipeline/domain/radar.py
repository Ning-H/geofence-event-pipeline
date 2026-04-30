from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from geofence_pipeline.domain.events import GeofenceEvent, GeofenceEventType

RADAR_GEOFENCE_EVENT_TYPES = {
    "user.entered_geofence": GeofenceEventType.ENTER,
    "user.exited_geofence": GeofenceEventType.EXIT,
}


def normalize_radar_webhook(payload: dict[str, Any]) -> list[GeofenceEvent]:
    events = payload.get("events")
    if events is None and payload.get("event"):
        events = [payload["event"]]
    if events is None:
        events = []

    root_user = payload.get("user") or {}
    normalized = []
    for event in events:
        event_type = RADAR_GEOFENCE_EVENT_TYPES.get(event.get("type"))
        if not event_type:
            continue
        normalized.append(_normalize_geofence_event(event, root_user, event_type))
    return normalized


def _normalize_geofence_event(
    event: dict[str, Any],
    root_user: dict[str, Any],
    event_type: GeofenceEventType,
) -> GeofenceEvent:
    user = event.get("user") or root_user
    geofence = event.get("geofence") or {}
    lat, lng = _extract_lat_lng(event)
    geofence_id = _geofence_id(geofence)

    return GeofenceEvent(
        event_id=event.get("_id") or event.get("id") or str(uuid4()),
        device_id=user.get("userId") or user.get("deviceId") or "unknown",
        geofence_id=geofence_id,
        geofence_name=geofence.get("description") or geofence_id,
        event_type=event_type,
        lat=lat,
        lng=lng,
        timestamp=_parse_timestamp(
            event.get("actualCreatedAt") or event.get("createdAt")
        ),
        dwell_time_seconds=_extract_dwell_time(event),
    )


def _extract_lat_lng(event: dict[str, Any]) -> tuple[float, float]:
    coordinates = (event.get("location") or {}).get("coordinates") or [0, 0]
    lng, lat = coordinates[:2]
    return float(lat), float(lng)


def _geofence_id(geofence: dict[str, Any]) -> str:
    tag = geofence.get("tag")
    external_id = geofence.get("externalId")
    if tag and external_id:
        return f"{tag}:{external_id}"
    return external_id or tag or geofence.get("_id") or "unknown"


def _parse_timestamp(value: str | None) -> datetime:
    if not value:
        return datetime.now(UTC)
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _extract_dwell_time(event: dict[str, Any]) -> float | None:
    for key in ("dwellTime", "dwell_time", "dwellTimeSeconds", "dwell_time_seconds"):
        value = event.get(key)
        if value is not None:
            return float(value)
    return None
