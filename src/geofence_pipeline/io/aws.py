import boto3
from botocore.config import Config
from geofence_pipeline.config.settings import get_settings


def boto3_client(service_name: str):
    settings = get_settings()
    return boto3.client(
        service_name,
        region_name=settings.aws_region,
        endpoint_url=settings.aws_endpoint_url,
        aws_access_key_id="test" if settings.aws_endpoint_url else None,
        aws_secret_access_key="test" if settings.aws_endpoint_url else None,
        config=Config(retries={"max_attempts": 10, "mode": "standard"}),
    )


def boto3_resource(service_name: str):
    settings = get_settings()
    return boto3.resource(
        service_name,
        region_name=settings.aws_region,
        endpoint_url=settings.aws_endpoint_url,
        aws_access_key_id="test" if settings.aws_endpoint_url else None,
        aws_secret_access_key="test" if settings.aws_endpoint_url else None,
        config=Config(retries={"max_attempts": 10, "mode": "standard"}),
    )
