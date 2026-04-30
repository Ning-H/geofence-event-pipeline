from geofence_pipeline.domain.events import GeofenceEventType
from geofence_pipeline.domain.radar import normalize_radar_webhook


def test_normalize_radar_geofence_webhook():
    payload = {
        "events": [
            {
                "_id": "evt_1",
                "type": "user.entered_geofence",
                "createdAt": "2026-04-30T12:00:00.000Z",
                "user": {"userId": "user_1"},
                "geofence": {
                    "tag": "store",
                    "externalId": "123",
                    "description": "Store 123",
                },
                "location": {"type": "Point", "coordinates": [-73.9855, 40.7580]},
            },
            {
                "_id": "evt_2",
                "type": "user.entered_place",
                "createdAt": "2026-04-30T12:00:01.000Z",
            },
        ],
        "user": {"userId": "root_user"},
    }

    events = normalize_radar_webhook(payload)

    assert len(events) == 1
    assert events[0].event_id == "evt_1"
    assert events[0].device_id == "user_1"
    assert events[0].geofence_id == "store:123"
    assert events[0].geofence_name == "Store 123"
    assert events[0].event_type == GeofenceEventType.ENTER
    assert events[0].lat == 40.7580
    assert events[0].lng == -73.9855
