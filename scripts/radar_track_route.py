import argparse
import json
import logging
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from geofence_pipeline.config.settings import get_settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


NYC_TRACK_POINTS = [
    ("times_square", 40.7580, -73.9855),
    ("grand_central", 40.7527, -73.9772),
    ("union_square", 40.7360, -73.9911),
    ("brooklyn_bridge", 40.7061, -73.9969),
    ("central_park", 40.7812, -73.9665),
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Send sample track calls to Radar /v1/track")
    parser.add_argument("--user-id", default="phase2_demo_user")
    parser.add_argument("--sleep", type=float, default=2.0)
    parser.add_argument("--loop", action="store_true")
    args = parser.parse_args()

    settings = get_settings()
    if not settings.radar_publishable_key:
        raise SystemExit("Set RADAR_PUBLISHABLE_KEY in .env before calling Radar /track")

    while True:
        for label, lat, lng in NYC_TRACK_POINTS:
            response = track(
                settings.radar_track_url,
                settings.radar_publishable_key,
                args.user_id,
                lat,
                lng,
            )
            logger.info(
                "Tracked %s lat=%s lng=%s status=%s",
                label,
                lat,
                lng,
                response.get("status"),
            )
            time.sleep(args.sleep)
        if not args.loop:
            return


def track(url: str, publishable_key: str, user_id: str, lat: float, lng: float) -> dict:
    payload = {
        "userId": user_id,
        "latitude": lat,
        "longitude": lng,
        "accuracy": 20,
    }
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": publishable_key,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8")
        raise RuntimeError(f"Radar track failed: HTTP {exc.code}: {body}") from exc


if __name__ == "__main__":
    main()
