from collections.abc import Iterable
from datetime import datetime
from io import BytesIO
from uuid import uuid4

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from geofence_pipeline.domain.events import GeofenceEvent, LocationPing
from geofence_pipeline.io.aws import boto3_client


class S3ParquetSink:
    def __init__(self, bucket: str):
        self.bucket = bucket
        self.client = boto3_client("s3")

    def write_raw_pings(self, pings: Iterable[LocationPing]) -> str | None:
        rows = [ping.model_dump(mode="json") for ping in pings]
        if not rows:
            return None
        ts = datetime.fromisoformat(rows[0]["timestamp"].replace("Z", "+00:00"))
        key = (
            f"raw-pings/year={ts:%Y}/month={ts:%m}/day={ts:%d}/hour={ts:%H}/"
            f"pings-{uuid4()}.parquet"
        )
        self._write_rows(key, rows)
        return key

    def write_geofence_events(self, events: Iterable[GeofenceEvent]) -> str | None:
        rows = [event.model_dump(mode="json") for event in events]
        if not rows:
            return None
        ts = datetime.fromisoformat(rows[0]["timestamp"].replace("Z", "+00:00"))
        key = (
            f"geofence-events/year={ts:%Y}/month={ts:%m}/day={ts:%d}/"
            f"events-{uuid4()}.parquet"
        )
        self._write_rows(key, rows)
        return key

    def _write_rows(self, key: str, rows: list[dict]) -> None:
        table = pa.Table.from_pandas(pd.DataFrame(rows), preserve_index=False)
        buffer = BytesIO()
        pq.write_table(table, buffer, compression="snappy")
        buffer.seek(0)
        self.client.put_object(Bucket=self.bucket, Key=key, Body=buffer.read())
