import argparse
import itertools
import logging
import time

from geofence_pipeline.config.settings import get_settings
from geofence_pipeline.io.kinesis import KinesisProducer
from geofence_pipeline.simulator.routes import create_devices

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulate NYC device pings into Kinesis")
    parser.add_argument("--devices", type=int, default=None)
    parser.add_argument("--max-events", type=int, default=None)
    args = parser.parse_args()

    settings = get_settings()
    devices = create_devices(args.devices or settings.simulator_device_count)
    device_cycle = itertools.cycle(devices)
    producer = KinesisProducer(settings.kinesis_stream_name)
    emitted = 0

    logger.info("Starting simulator with %s devices", len(devices))
    while True:
        batch = [
            next(device_cycle).next_ping()
            for _ in range(settings.simulator_batch_size)
        ]
        producer.put_pings(batch)
        emitted += len(batch)
        logger.info("Published %s pings (total=%s)", len(batch), emitted)

        max_events = (
            args.max_events if args.max_events is not None else settings.simulator_max_events
        )
        if max_events is not None and emitted >= max_events:
            logger.info("Reached max events; stopping simulator")
            return
        time.sleep(settings.simulator_interval_seconds)


if __name__ == "__main__":
    main()
