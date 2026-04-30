from io import BytesIO

import pyarrow.parquet as pq
from geofence_pipeline.config.settings import get_settings
from geofence_pipeline.io.aws import boto3_client


def main() -> None:
    settings = get_settings()
    preview_latest_parquet(settings.s3_bucket, "raw-pings/")
    preview_latest_parquet(settings.s3_bucket, "geofence-events/")


def preview_latest_parquet(bucket: str, prefix: str) -> None:
    client = boto3_client("s3")
    response = client.list_objects_v2(Bucket=bucket, Prefix=prefix)
    objects = [
        obj for obj in response.get("Contents", [])
        if obj["Key"].endswith(".parquet")
    ]

    print(f"\ns3://{bucket}/{prefix}")
    if not objects:
        print("  no parquet files found")
        return

    latest = max(objects, key=lambda obj: obj["LastModified"])
    body = client.get_object(Bucket=bucket, Key=latest["Key"])["Body"].read()
    table = pq.read_table(BytesIO(body))
    frame = table.to_pandas().head(5)

    print(f"  latest file: {latest['Key']}")
    print(frame.to_string(index=False))


if __name__ == "__main__":
    main()
