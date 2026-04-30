from datetime import datetime

from geofence_pipeline.domain.events import (
    DeviceGeofenceState,
    GeofenceEvent,
    GeofenceEventType,
    LocationPing,
)
from geofence_pipeline.domain.geofences import Geofence


class GeofenceDetector:
    def __init__(self, geofences: list[Geofence]):
        self.geofences = geofences
        self.state_by_device: dict[str, DeviceGeofenceState] = {}

    def process_ping(self, ping: LocationPing) -> list[GeofenceEvent]:
        matching = self._first_containing_geofence(ping.lat, ping.lng)
        previous = self.state_by_device.get(ping.device_id)
        previous_geofence_id = previous.current_geofence_id if previous else None
        events: list[GeofenceEvent] = []

        changed_geofence = matching is None or matching.geofence_id != previous_geofence_id
        if previous_geofence_id and changed_geofence:
            events.append(self._exit_event(ping, previous))

        if matching and matching.geofence_id != previous_geofence_id:
            events.append(
                GeofenceEvent(
                    device_id=ping.device_id,
                    geofence_id=matching.geofence_id,
                    geofence_name=matching.name,
                    event_type=GeofenceEventType.ENTER,
                    lat=ping.lat,
                    lng=ping.lng,
                    timestamp=ping.timestamp,
                )
            )

        self.state_by_device[ping.device_id] = DeviceGeofenceState(
            device_id=ping.device_id,
            current_geofence_id=matching.geofence_id if matching else None,
            current_geofence_name=matching.name if matching else None,
            entry_time=self._entry_time(
                previous,
                matching.geofence_id if matching else None,
                ping.timestamp,
            ),
            last_seen=ping.timestamp,
            lat=ping.lat,
            lng=ping.lng,
        )
        return events

    def get_state(self, device_id: str) -> DeviceGeofenceState | None:
        return self.state_by_device.get(device_id)

    def _first_containing_geofence(self, lat: float, lng: float) -> Geofence | None:
        return next((geofence for geofence in self.geofences if geofence.contains(lat, lng)), None)

    @staticmethod
    def _entry_time(
        previous: DeviceGeofenceState | None,
        current_geofence_id: str | None,
        timestamp: datetime,
    ) -> datetime | None:
        if current_geofence_id is None:
            return None
        if previous and previous.current_geofence_id == current_geofence_id:
            return previous.entry_time
        return timestamp

    @staticmethod
    def _exit_event(ping: LocationPing, previous: DeviceGeofenceState) -> GeofenceEvent:
        dwell_time = None
        if previous.entry_time:
            dwell_time = max((ping.timestamp - previous.entry_time).total_seconds(), 0)

        return GeofenceEvent(
            device_id=ping.device_id,
            geofence_id=previous.current_geofence_id or "",
            geofence_name=previous.current_geofence_name or "",
            event_type=GeofenceEventType.EXIT,
            lat=ping.lat,
            lng=ping.lng,
            timestamp=ping.timestamp,
            dwell_time_seconds=dwell_time,
        )
