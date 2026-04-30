CREATE EXTERNAL TABLE IF NOT EXISTS radar_pipeline.raw_pings (
  device_id string,
  lat double,
  lng double,
  timestamp timestamp,
  speed double
)
PARTITIONED BY (
  year string,
  month string,
  day string,
  hour string
)
STORED AS PARQUET
LOCATION 's3://radar-pipeline/raw-pings/';

CREATE EXTERNAL TABLE IF NOT EXISTS radar_pipeline.geofence_events (
  event_id string,
  device_id string,
  geofence_id string,
  geofence_name string,
  event_type string,
  lat double,
  lng double,
  timestamp timestamp,
  dwell_time_seconds double
)
PARTITIONED BY (
  year string,
  month string,
  day string
)
STORED AS PARQUET
LOCATION 's3://radar-pipeline/geofence-events/';

MSCK REPAIR TABLE radar_pipeline.raw_pings;
MSCK REPAIR TABLE radar_pipeline.geofence_events;
