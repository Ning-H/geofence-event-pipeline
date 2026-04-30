import argparse
import logging
import time

from geofence_pipeline.config.settings import get_settings
from geofence_pipeline.domain.events import DeviceGeofenceState, GeofenceEventType
from geofence_pipeline.io.dynamodb import DeviceStateRepository
from geofence_pipeline.io.kinesis import KinesisConsumer
from geofence_pipeline.io.parquet import S3ParquetSink

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="Consume normalized Radar geofence events")
    parser.add_argument("--flush-size", type=int, default=25)
    args = parser.parse_args()

    settings = get_settings()
    consumer = KinesisConsumer(settings.radar_event_stream_name)
    parquet_sink = S3ParquetSink(settings.s3_bucket)
    state_repo = DeviceStateRepository(settings.dynamodb_table)
    event_buffer = []

    logger.info("Starting Radar event consumer for stream=%s", settings.radar_event_stream_name)
    for event in consumer.iter_geofence_events():
        event_buffer.append(event)
        state_repo.put_state(_state_from_event(event))
        logger.info(
            "Radar %s device=%s geofence=%s",
            event.event_type,
            event.device_id,
            event.geofence_id,
        )

        if len(event_buffer) >= args.flush_size:
            parquet_sink.write_geofence_events(event_buffer)
            event_buffer.clear()

        time.sleep(0.1)


def _state_from_event(event) -> DeviceGeofenceState:
    inside = event.event_type == GeofenceEventType.ENTER
    return DeviceGeofenceState(
        device_id=event.device_id,
        current_geofence_id=event.geofence_id if inside else None,
        current_geofence_name=event.geofence_name if inside else None,
        entry_time=event.timestamp if inside else None,
        last_seen=event.timestamp,
        lat=event.lat,
        lng=event.lng,
    )


if __name__ == "__main__":
    main()
