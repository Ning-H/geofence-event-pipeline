import hashlib
import hmac
import json
from datetime import UTC, datetime
from urllib.request import Request, urlopen
from uuid import uuid4

from geofence_pipeline.config.settings import get_settings


def main() -> None:
    settings = get_settings()
    body = json.dumps(sample_payload()).encode("utf-8")
    signing_id = str(uuid4())
    signature = hmac.new(
        settings.radar_webhook_secret.encode("utf-8"),
        signing_id.encode("utf-8"),
        hashlib.sha1,
    ).hexdigest()

    request = Request(
        "http://localhost:8000/webhooks/radar",
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-Radar-Signing-Id": signing_id,
            "X-Radar-Signature": signature,
        },
        method="POST",
    )
    with urlopen(request, timeout=10) as response:
        print(response.read().decode("utf-8"))


def sample_payload() -> dict:
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    return {
        "events": [
            {
                "_id": str(uuid4()),
                "type": "user.entered_geofence",
                "createdAt": now,
                "actualCreatedAt": now,
                "user": {"userId": "phase2_demo_user", "deviceId": "demo_device"},
                "geofence": {
                    "tag": "store",
                    "externalId": "times-square-demo",
                    "description": "Times Square Demo Geofence",
                },
                "location": {
                    "type": "Point",
                    "coordinates": [-73.9855, 40.7580],
                },
                "confidence": 3,
            },
            {
                "_id": str(uuid4()),
                "type": "user.exited_geofence",
                "createdAt": now,
                "actualCreatedAt": now,
                "user": {"userId": "phase2_demo_user", "deviceId": "demo_device"},
                "geofence": {
                    "tag": "store",
                    "externalId": "times-square-demo",
                    "description": "Times Square Demo Geofence",
                },
                "location": {
                    "type": "Point",
                    "coordinates": [-73.9800, 40.7600],
                },
                "confidence": 3,
            },
        ],
        "user": {"userId": "phase2_demo_user", "deviceId": "demo_device"},
    }


if __name__ == "__main__":
    main()
