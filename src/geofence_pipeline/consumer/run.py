import argparse
import logging
import time

from geofence_pipeline.config.settings import get_settings
from geofence_pipeline.domain.detector import GeofenceDetector
from geofence_pipeline.domain.geofences import load_nyc_geofences
from geofence_pipeline.io.dynamodb import DeviceStateRepository
from geofence_pipeline.io.kinesis import KinesisConsumer
from geofence_pipeline.io.parquet import S3ParquetSink

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="Consume Kinesis pings and emit geofence events")
    parser.add_argument("--flush-size", type=int, default=50)
    args = parser.parse_args()

    settings = get_settings()
    detector = GeofenceDetector(load_nyc_geofences())
    consumer = KinesisConsumer(settings.kinesis_stream_name)
    parquet_sink = S3ParquetSink(settings.s3_bucket)
    state_repo = DeviceStateRepository(settings.dynamodb_table)

    raw_buffer = []
    event_buffer = []

    logger.info("Starting consumer for stream=%s", settings.kinesis_stream_name)
    for ping in consumer.iter_pings():
        raw_buffer.append(ping)
        events = detector.process_ping(ping)
        event_buffer.extend(events)

        state = detector.get_state(ping.device_id)
        if state:
            state_repo.put_state(state)

        for event in events:
            logger.info(
                "Detected %s device=%s geofence=%s dwell=%s",
                event.event_type,
                event.device_id,
                event.geofence_id,
                event.dwell_time_seconds,
            )

        if len(raw_buffer) >= args.flush_size:
            parquet_sink.write_raw_pings(raw_buffer)
            raw_buffer.clear()

        if len(event_buffer) >= args.flush_size:
            parquet_sink.write_geofence_events(event_buffer)
            event_buffer.clear()

        time.sleep(0.1)


if __name__ == "__main__":
    main()
