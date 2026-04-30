from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class LocationPing(BaseModel):
    device_id: str
    lat: float
    lng: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    speed: float

    def partition_key(self) -> str:
        return self.device_id


class GeofenceEventType(StrEnum):
    ENTER = "ENTER"
    EXIT = "EXIT"


class GeofenceEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    device_id: str
    geofence_id: str
    geofence_name: str
    event_type: GeofenceEventType
    lat: float
    lng: float
    timestamp: datetime
    dwell_time_seconds: float | None = None


class DeviceGeofenceState(BaseModel):
    device_id: str
    current_geofence_id: str | None = None
    current_geofence_name: str | None = None
    entry_time: datetime | None = None
    last_seen: datetime
    lat: float
    lng: float

    def dynamodb_item(self) -> dict[str, Any]:
        return {
            "device_id": self.device_id,
            "current_geofence_id": self.current_geofence_id or "",
            "current_geofence_name": self.current_geofence_name or "",
            "entry_time": self.entry_time.isoformat() if self.entry_time else "",
            "last_seen": self.last_seen.isoformat(),
            "lat": str(self.lat),
            "lng": str(self.lng),
        }
