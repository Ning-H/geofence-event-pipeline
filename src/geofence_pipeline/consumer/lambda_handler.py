import base64
import json
import logging

from geofence_pipeline.config.settings import get_settings
from geofence_pipeline.domain.detector import GeofenceDetector
from geofence_pipeline.domain.events import LocationPing
from geofence_pipeline.domain.geofences import load_nyc_geofences
from geofence_pipeline.io.dynamodb import DeviceStateRepository
from geofence_pipeline.io.parquet import S3ParquetSink

logger = logging.getLogger(__name__)
settings = get_settings()
detector = GeofenceDetector(load_nyc_geofences())
parquet_sink = S3ParquetSink(settings.s3_bucket)
state_repo = DeviceStateRepository(settings.dynamodb_table)


def handler(event, context):
    pings = []
    geofence_events = []

    for record in event.get("Records", []):
        payload = _decode_record(record)
        ping = LocationPing.model_validate(payload)
        pings.append(ping)
        geofence_events.extend(detector.process_ping(ping))

        state = detector.get_state(ping.device_id)
        if state:
            state_repo.put_state(state)

    raw_key = parquet_sink.write_raw_pings(pings)
    event_key = parquet_sink.write_geofence_events(geofence_events)
    logger.info(
        "Processed records=%s geofence_events=%s raw_key=%s event_key=%s",
        len(pings),
        len(geofence_events),
        raw_key,
        event_key,
    )
    return {"records": len(pings), "geofence_events": len(geofence_events)}


def _decode_record(record: dict) -> dict:
    data = record["kinesis"]["data"]
    decoded = base64.b64decode(data).decode("utf-8")
    return json.loads(decoded)
