import logging

from botocore.exceptions import ClientError
from geofence_pipeline.config.settings import get_settings
from geofence_pipeline.io.aws import boto3_client

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    settings = get_settings()
    create_stream(settings.kinesis_stream_name)
    create_stream(settings.radar_event_stream_name)
    create_bucket(settings.s3_bucket)
    create_device_state_table(settings.dynamodb_table)


def create_stream(stream_name: str) -> None:
    client = boto3_client("kinesis")
    try:
        client.create_stream(StreamName=stream_name, ShardCount=1)
        logger.info("Created Kinesis stream %s", stream_name)
    except ClientError as exc:
        if exc.response["Error"]["Code"] != "ResourceInUseException":
            raise
        logger.info("Kinesis stream %s already exists", stream_name)


def create_bucket(bucket: str) -> None:
    client = boto3_client("s3")
    try:
        client.create_bucket(Bucket=bucket)
        logger.info("Created S3 bucket %s", bucket)
    except ClientError as exc:
        if exc.response["Error"]["Code"] not in {"BucketAlreadyExists", "BucketAlreadyOwnedByYou"}:
            raise
        logger.info("S3 bucket %s already exists", bucket)


def create_device_state_table(table_name: str) -> None:
    client = boto3_client("dynamodb")
    try:
        client.create_table(
            TableName=table_name,
            BillingMode="PAY_PER_REQUEST",
            AttributeDefinitions=[{"AttributeName": "device_id", "AttributeType": "S"}],
            KeySchema=[{"AttributeName": "device_id", "KeyType": "HASH"}],
        )
        logger.info("Created DynamoDB table %s", table_name)
    except ClientError as exc:
        if exc.response["Error"]["Code"] != "ResourceInUseException":
            raise
        logger.info("DynamoDB table %s already exists", table_name)


if __name__ == "__main__":
    main()
