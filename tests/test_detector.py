from datetime import UTC, datetime, timedelta

from geofence_pipeline.domain.detector import GeofenceDetector
from geofence_pipeline.domain.events import GeofenceEventType, LocationPing
from geofence_pipeline.domain.geofences import load_nyc_geofences


def test_detector_emits_enter_and_exit():
    detector = GeofenceDetector(load_nyc_geofences())
    start = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)

    enter_ping = LocationPing(
        device_id="device_1",
        lat=40.7580,
        lng=-73.9855,
        timestamp=start,
        speed=3.2,
    )
    events = detector.process_ping(enter_ping)
    assert len(events) == 1
    assert events[0].event_type == GeofenceEventType.ENTER
    assert events[0].geofence_id == "times_square"

    exit_ping = LocationPing(
        device_id="device_1",
        lat=40.7300,
        lng=-73.9900,
        timestamp=start + timedelta(minutes=7),
        speed=4.1,
    )
    events = detector.process_ping(exit_ping)
    assert len(events) == 1
    assert events[0].event_type == GeofenceEventType.EXIT
    assert events[0].dwell_time_seconds == 420


def test_detector_no_duplicate_enter_while_inside():
    detector = GeofenceDetector(load_nyc_geofences())
    start = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)

    detector.process_ping(
        LocationPing(
            device_id="device_1",
            lat=40.7580,
            lng=-73.9855,
            timestamp=start,
            speed=3.2,
        )
    )
    events = detector.process_ping(
        LocationPing(
            device_id="device_1",
            lat=40.7582,
            lng=-73.9857,
            timestamp=start + timedelta(seconds=30),
            speed=2.9,
        )
    )
    assert events == []
