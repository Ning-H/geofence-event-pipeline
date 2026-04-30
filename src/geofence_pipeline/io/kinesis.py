import json
import logging
from collections.abc import Iterable

from botocore.exceptions import ClientError
from geofence_pipeline.domain.events import GeofenceEvent, LocationPing
from geofence_pipeline.io.aws import boto3_client

logger = logging.getLogger(__name__)


class KinesisProducer:
    def __init__(self, stream_name: str):
        self.stream_name = stream_name
        self.client = boto3_client("kinesis")

    def put_pings(self, pings: Iterable[LocationPing]) -> None:
        self.put_json_records(
            (ping.model_dump(mode="json") for ping in pings),
            partition_key_fn=lambda row: row["device_id"],
        )

    def put_geofence_events(self, events: Iterable[GeofenceEvent]) -> None:
        self.put_json_records(
            (event.model_dump(mode="json") for event in events),
            partition_key_fn=lambda row: row["device_id"],
        )

    def put_json_records(self, rows: Iterable[dict], partition_key_fn) -> None:
        records = []
        for row in rows:
            records.append(
                {
                    "Data": json.dumps(row, default=str).encode("utf-8"),
                    "PartitionKey": partition_key_fn(row),
                }
            )
        self._put_records(records)

    def _put_records(self, records: list[dict]) -> None:
        for start in range(0, len(records), 500):
            batch = records[start:start + 500]
            if not batch:
                continue
            response = self.client.put_records(StreamName=self.stream_name, Records=batch)
            failed = response.get("FailedRecordCount", 0)
            if failed:
                logger.warning("Kinesis put_records had %s failed records", failed)


class KinesisConsumer:
    def __init__(self, stream_name: str):
        self.stream_name = stream_name
        self.client = boto3_client("kinesis")

    def iter_pings(self):
        for payload in self.iter_json_records():
            yield LocationPing.model_validate(payload)

    def iter_geofence_events(self):
        for payload in self.iter_json_records():
            yield GeofenceEvent.model_validate(payload)

    def iter_json_records(self):
        stream = self.client.describe_stream(StreamName=self.stream_name)["StreamDescription"]
        shard_ids = [shard["ShardId"] for shard in stream["Shards"]]
        iterators = {
            shard_id: self._get_iterator(shard_id)
            for shard_id in shard_ids
        }

        while True:
            for shard_id, iterator in list(iterators.items()):
                if not iterator:
                    continue
                try:
                    response = self.client.get_records(ShardIterator=iterator, Limit=100)
                except ClientError:
                    logger.exception("Failed reading Kinesis shard %s", shard_id)
                    continue
                iterators[shard_id] = response.get("NextShardIterator")
                for record in response.get("Records", []):
                    yield json.loads(record["Data"].decode("utf-8"))

    def _get_iterator(self, shard_id: str) -> str:
        response = self.client.get_shard_iterator(
            StreamName=self.stream_name,
            ShardId=shard_id,
            ShardIteratorType="LATEST",
        )
        return response["ShardIterator"]
