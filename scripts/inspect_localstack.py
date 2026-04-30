import argparse

from geofence_pipeline.config.settings import get_settings
from geofence_pipeline.io.aws import boto3_client


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect LocalStack pipeline outputs")
    parser.add_argument("--dynamodb", action="store_true", help="Print device_state rows")
    args = parser.parse_args()

    settings = get_settings()
    list_s3_prefix(settings.s3_bucket, "raw-pings/")
    list_s3_prefix(settings.s3_bucket, "geofence-events/")
    if args.dynamodb:
        scan_device_state(settings.dynamodb_table)


def list_s3_prefix(bucket: str, prefix: str) -> None:
    client = boto3_client("s3")
    print(f"\ns3://{bucket}/{prefix}")
    response = client.list_objects_v2(Bucket=bucket, Prefix=prefix)
    objects = response.get("Contents", [])
    if not objects:
        print("  no objects found")
        return
    for obj in objects:
        print(f"  {obj['Size']:>8} bytes  {obj['Key']}")


def scan_device_state(table_name: str) -> None:
    client = boto3_client("dynamodb")
    print(f"\nDynamoDB table: {table_name}")
    response = client.scan(TableName=table_name, Limit=20)
    items = response.get("Items", [])
    if not items:
        print("  no rows found")
        return
    for item in items:
        device_id = item["device_id"]["S"]
        geofence = item.get("current_geofence_name", {}).get("S", "")
        last_seen = item.get("last_seen", {}).get("S", "")
        print(f"  {device_id}  geofence={geofence or 'outside'}  last_seen={last_seen}")


if __name__ == "__main__":
    main()
