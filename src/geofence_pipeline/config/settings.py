from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    aws_region: str = "us-east-1"
    aws_endpoint_url: str | None = "http://localhost:4566"

    kinesis_stream_name: str = "location-pings"
    radar_event_stream_name: str = "radar-geofence-events"
    s3_bucket: str = "radar-pipeline-local"
    dynamodb_table: str = "device_state"

    simulator_device_count: int = 75
    simulator_interval_seconds: float = 1.5
    simulator_batch_size: int = 25
    simulator_max_events: int | None = 500

    radar_webhook_secret: str = "replace-me"
    radar_validate_signature: bool = False
    radar_publishable_key: str = ""
    radar_track_url: str = "https://api.radar.io/v1/track"


@lru_cache
def get_settings() -> Settings:
    return Settings()
